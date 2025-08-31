# tools/excel_reader.py
from __future__ import annotations

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from langchain.tools import BaseTool

from .openai_utils import llm_json_infer  # OpenAI-powered inference

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Fuzzy header map
CANON_KEYS = {
    "description": ["kpi requirement", "requirement", "description", "desc", "kpi", "kpi requirement / description"],
    "component":   ["component", "component name", "ui element", "element", "control", "widget"],
    "action":      ["action", "event", "trigger", "action / event"],
    "page":        ["page", "route", "screen", "view", "context"],
    "adobe_var":   ["adobe variables", "adobe variable", "variable", "evar", "prop", "vars"],
    "adobe_val":   ["adobe values", "adobe value", "value", "val"],
    "screenshot":  ["screenshot", "image", "img", "figure", "picture"],
}

# lightweight local heuristics (used when use_llm=False or as fallback)
ACTION_WORDS = {
    "click": ["click", "tap", "press"],
    "submit": ["submit", "form submit", "save"],
    "view": ["view", "page view", "load", "mount", "pageview"],
    "back": ["back"],
    "exit": ["exit", "close", "quit"],
    "select": ["select", "choose", "pick"],
    "nav": ["nav", "navigate", "route", "go to", "open"],
}

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()

def _find_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    norm_cols = {c: _norm(c) for c in cols}
    for target in candidates:
        for original, normed in norm_cols.items():
            if target in normed:
                return original
    return None

def _extract_page_from_brackets(text: str) -> Optional[str]:
    m = re.match(r"\s*\[([^\]]+)\]", str(text))
    return m.group(1).strip() if m else None

def _local_infer_action(texts: List[str]) -> Optional[str]:
    t = " ".join([_norm(x) for x in texts if x])
    for action, keys in ACTION_WORDS.items():
        for k in keys:
            if f" {k} " in f" {t} ":
                return action
    return None

def _phrases_in_quotes(text: str) -> List[str]:
    return [p.strip() for p in re.findall(r"[\"“”']([^\"“”']+)[\"“”']", str(text) or "") if p.strip()]

def _fallback_terms(text: str) -> List[str]:
    toks = [w for w in re.split(r"[^A-Za-z0-9]+", str(text) or "") if 2 <= len(w) <= 24]
    uiish = [w for w in toks if w[0].isupper() or w.lower() in {"back", "exit", "mobile"}]
    out, seen = [], set()
    for w in uiish:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out[:4]

def _terms_from_row(description: str, component: Optional[str], adobe_val: Optional[str]) -> List[str]:
    terms: List[str] = []
    terms += _phrases_in_quotes(description)
    if component:
        terms += _phrases_in_quotes(component)
        if not terms:
            terms += _fallback_terms(component)
    if adobe_val and not terms:
        nice = re.sub(r"[_\-]+", " ", adobe_val)
        terms += _fallback_terms(nice)
    if not terms:
        terms += _fallback_terms(description)
    # unique, keep order
    out, seen = [], set()
    for t in terms:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

class ExcelReaderTool(BaseTool):
    """
    Reads an Excel tech spec (multi-sheet, flexible headers) and returns normalized rows.
    
    Optional OpenAI inference improves action/page/target_terms.

    _run(excel_path: str, use_llm: bool = False)
    """
    name = "excel_reader"
    description = "Normalize tech spec Excel into actionable spec_items (with optional OpenAI inference)."

    def _run(self, excel_path: str, use_llm: bool = False) -> Dict[str, Any]:
        try:
            items, sheets = self._parse_excel_any_layout(excel_path, use_llm=use_llm)
            return {
                "status": "success",
                "sheets_parsed": sheets,
                "spec_items": items,
                "summary": {"items": len(items), "llm_used": bool(use_llm)},
            }
        except Exception as e:
            logger.exception(f"ExcelReaderTool failed: {e}")
            return {"status": "error", "error": str(e)}

    # ---- parsing ----

    def _parse_excel_any_layout(self, excel_path: str, use_llm: bool) -> Tuple[List[Dict[str, Any]], List[str]]:
        path = Path(excel_path)
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        xls = pd.ExcelFile(str(path))
        parsed: List[Dict[str, Any]] = []
        parsed_sheets: List[str] = []

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            if df.empty:
                continue

            colmap = self._detect_columns(list(df.columns))
            if not any(colmap.values()):
                logger.info(f"[ExcelReader] Skipping sheet '{sheet}' — no recognizable columns.")
                continue

            parsed_sheets.append(sheet)

            for ridx, row in df.iterrows():
                desc = str(row.get(colmap["description"], "")).strip() if colmap["description"] else ""
                comp = str(row.get(colmap["component"], "")).strip() if colmap["component"] else None
                act  = str(row.get(colmap["action"], "")).strip() if colmap["action"] else None
                page = str(row.get(colmap["page"], "")).strip() if colmap["page"] else None
                avar = str(row.get(colmap["adobe_var"], "")).strip() if colmap["adobe_var"] else None
                aval = str(row.get(colmap["adobe_val"], "")).strip() if colmap["adobe_val"] else None
                shot = str(row.get(colmap["screenshot"], "")).strip() if colmap["screenshot"] else None

                if not desc and not comp and not aval:
                    continue

                page = page or _extract_page_from_brackets(desc)

                if use_llm:
                    inferred = llm_json_infer({
                        "sheet": sheet,
                        "row_index": ridx + 2,
                        "description": desc,
                        "component": comp,
                        "action_hint": act,
                        "page_hint": page,
                        "adobe_var": avar,
                        "adobe_value": aval,
                    })
                    action = inferred.get("action") or _local_infer_action([act, desc, aval])
                    terms  = inferred.get("target_terms") or _terms_from_row(desc or comp or "", comp, aval)
                    page   = inferred.get("page") or page
                else:
                    action = _local_infer_action([act, desc, aval])
                    terms  = _terms_from_row(desc or comp or "", comp, aval)

                parsed.append({
                    "sheet": sheet,
                    "row_index": (ridx + 2),
                    "description": desc or (comp or ""),
                    "component": comp or None,
                    "action": action,
                    "page": page or None,
                    "adobe_var": avar or None,
                    "adobe_value": aval or None,
                    "screenshot": shot or None,
                    "target_terms": terms,
                })

        if not parsed:
            raise ValueError("No valid rows found in the Excel file.")
        return parsed, parsed_sheets

    def _detect_columns(self, columns: List[str]) -> Dict[str, Optional[str]]:
        mapping: Dict[str, Optional[str]] = {k: None for k in CANON_KEYS.keys()}
        for key, synonyms in CANON_KEYS.items():
            mapping[key] = _find_col(columns, synonyms)
        if not mapping["description"] and mapping["component"]:
            mapping["description"] = mapping["component"]
        return mapping
