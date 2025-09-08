# tools/agent.py
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

from tools.excelReader import ExcelReaderTool
from tools.repoMatcher import RepoMatcherTool
from tools.openai_utils import llm_explain_mapping
from tools.report_writer import to_markdown, take_window
from utils.file_handler import FileHandler
import logging

# Optional external suggester; fine if missing
try:
    from tools.code_suggester import (
        suggest_click_like_code,
        suggest_view_code,
        suggest_track_helper,
    )
    _HAS_SUGGESTER = True
except Exception:
    _HAS_SUGGESTER = False

logging.basicConfig(level=logging.INFO)
def _slug(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[^\w]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_").lower()


def _fallback_track_helper():
    file_path = "src/analytics/track.js"
    contents = (
        "// src/analytics/track.js\n"
        "export function track(eventName, params = {}) {\n"
        "  const s = window && window.s;\n"
        "  if (!s) {\n"
        "    // eslint-disable-next-line no-console\n"
        "    console.warn('[track] Adobe AppMeasurement `s` not found. Event:', eventName, params);\n"
        "    return;\n"
        "  }\n"
        "  const isPageView = !!params.__pv;\n"
        "  const { __pv, events, ...rest } = params;\n"
        "  const prevLinkTrackVars = s.linkTrackVars;\n"
        "  const prevLinkTrackEvents = s.linkTrackEvents;\n"
        "  try {\n"
        "    const varNames = [];\n"
        "    for (const [k, v] of Object.entries(rest)) {\n"
        "      if (/^(eVar|prop)\\d+$/i.test(k)) { s[k] = v; varNames.push(k); }\n"
        "      else if (k === 'pageName') { s.pageName = v; varNames.push('pageName'); }\n"
        "    }\n"
        "    if (isPageView) {\n"
        "      if (events) s.events = events; // e.g., 'event10'\n"
        "      s.t();               // page view call\n"
        "      s.clearVars();       // prevent bleed to next hit\n"
        "      return;\n"
        "    }\n"
        "    // Link tracking (CTA/click)\n"
        "    s.linkTrackVars = varNames.concat('events').join(',');\n"
        "    if (events) s.linkTrackEvents = events;\n"
        "    s.events = events || '';\n"
        "    s.tl(true, 'o', eventName);  // 'o' = custom link, name = eventName\n"
        "  } catch (e) {\n"
        "    // eslint-disable-next-line no-console\n"
        "    console.error('track error', e);\n"
        "  } finally {\n"
        "    s.linkTrackVars = prevLinkTrackVars;\n"
        "    s.linkTrackEvents = prevLinkTrackEvents;\n"
        "  }\n"
        "}\n"
    )
    return (file_path, contents)



def _fallback_click_code(event_name: str, params: Dict[str, Any], analytics_id: str) -> Dict[str, str]:
    # Ensure import path is JS:
    return {
        "imports": 'import { track } from "../analytics/track.js";',
        "jsx_attrs": (
            f'data-analytics-id="{analytics_id}"\n'
            "onClick={(e) => {\n"
            f"  track(\"{event_name}\", {json.dumps(params, indent=2)});\n"
            "  /* originalOnClick?.(e); */\n"
            "}}"
        ),
        "alt_handler_wrap": (
            "/* If the element uses a named handler like onClick={handleClick}, wrap it: */\n"
            "const _origHandleClick = typeof handleClick === 'function' ? handleClick : null;\n"
            "const handleClickTracked = (e) => {\n"
            f"  track(\"{event_name}\", {json.dumps(params, indent=2)});\n"
            "  if (_origHandleClick) return _origHandleClick(e);\n"
            "};\n"
            "/* then use: onClick={handleClickTracked} */"
        ),
    }


def _fallback_view_code(event_name: str, params: Dict[str, Any]) -> Dict[str, str]:
    # Force page view flag
    if "__pv" not in params:
        params = {**params, "__pv": True}
    return {
        "imports": "import { useEffect } from 'react';\nimport { track } from '../analytics/track.js';",
        "hook": (
            "useEffect(() => {\n"
            f"  track(\"{event_name}\", {json.dumps(params, indent=2)});\n"
            "}, []);"
        ),
    }



def load_repo_text_map(repo_path: str, react_files: List[str]) -> Dict[str, List[str]]:
    text_map = {}
    for f in react_files:
        text_map[f] = FileHandler.read_file_content(f).splitlines()
    return text_map


def build_unified(
    excel_path: str,
    repo_path: str,
    use_llm: bool = True,
) -> Dict[str, Any]:
    # 1) parse spec
    excel_tool = ExcelReaderTool()
    ex = excel_tool._run(excel_path, use_llm=use_llm)
    if ex.get("status") != "success":
        raise RuntimeError(f"ExcelReader failed: {ex}")

    spec_items = ex["spec_items"]
    for i, it in enumerate(spec_items):
        it["item_index"] = i

    # 2) scan repo
    repo_tool = RepoMatcherTool()
    rm = repo_tool._run(repo_path, spec_items, use_embeddings=use_llm)
    if rm.get("status") != "success":
        raise RuntimeError(f"RepoMatcher failed: {rm}")

    # Index file contents for snippets
    files = [s["matches"][0]["file"] for s in rm["suggestions"] if s.get("matches")]
    files = sorted(set(files))
    text_map = load_repo_text_map(repo_path, files)

    # 3) stitch into 1 unified structure
    run_id = time.strftime("%Y-%m-%dT%H:%M:%S")
    unified = {
        "run_id": run_id,
        "excel": str(Path(excel_path).resolve()),
        "repo": str(Path(repo_path).resolve()),
        "items": [],
    }

    # Optional helper file (track util) — JS version
    if _HAS_SUGGESTER:
        try:
            helper_path, helper_contents = suggest_track_helper()  # you can switch its content to JS in that file
        except Exception:
            helper_path, helper_contents = _fallback_track_helper()
    else:
        helper_path, helper_contents = _fallback_track_helper()
    # Ensure helper ends with .js
    if not helper_path.endswith(".js"):
        helper_path = helper_path.rsplit(".", 1)[0] + ".js"
    unified["helper_file"] = {"path": helper_path, "contents": helper_contents}

    for item, sug in zip(spec_items, rm["suggestions"]):
        row: Dict[str, Any] = {
            "sheet": item.get("sheet"),
            "row_index": item.get("row_index"),
            "page": item.get("page"),
            "action": item.get("action"),
            "kpi": item.get("description"),  # KPI = description column
            "adobe": {"var": item.get("adobe_var"), "value": item.get("adobe_value")},
            "target_terms": item.get("target_terms"),
        }

        if sug.get("matches"):
            top = sug["matches"][0]
            row["top_match"] = top

            # add snippet
            file = top["file"]
            line = top["line"]
            lines = text_map.get(file) or FileHandler.read_file_content(file).splitlines()
            snippet = take_window(lines, line, radius=6)
            row["snippet"] = snippet

            # 4) LLM explanation + event details (ask it to return JS code if possible)
            if use_llm:
                expl = llm_explain_mapping(item, top, snippet)  # system prompt is updated in openai_utils to produce JS
            else:
                expl = {
                    "kpi": row["kpi"],
                    "why_location": "Matched by visible label/terms and nearby onClick.",
                    "suggested_event_name": item.get("adobe_value") or "custom_event",
                    "suggested_params": {},
                    "implementation_note": "Call track(eventName, params) inside the handler.",
                    "risks": [],
                    "code": {},
                }

            row.update(expl)

            # --- Adobe param seeding (fallback-safe and also fixes weak LLM outputs) ---
            action = (row.get("action") or "").lower()

            # Event name: prefer LLM, else spec's adobe_value, else slug of KPI
            event_name = (
                row.get("suggested_event_name")
                or item.get("adobe_value")
                or _slug(row.get("kpi") or "custom_event")
                )

            # Start from LLM params if any, then layer Adobe var/value from spec
            params = dict(row.get("suggested_params") or {})
            adobe_var = (item.get("adobe_var") or "").strip()
            adobe_val = item.get("adobe_value")

            # Inject eVar/prop only if provided and not already present
            if adobe_var and adobe_val and adobe_var not in params:
                 params[adobe_var] = adobe_val

            # For page views, mark as PV and provide pageName when we have it
            if action == "view":
                params.setdefault("__pv", True)
            if item.get("page") and "pageName" not in params:
                 params["pageName"] = item["page"]

            # Write back so the report shows these and the fallback uses them
            row["suggested_event_name"] = event_name
            row["suggested_params"] = params
            
            # 5) Ensure there is paste-ready code (LLM or fallback)
            code_from_llm = expl.get("code") if isinstance(expl, dict) else None
            has_llm_code = isinstance(code_from_llm, dict) and any(
           (isinstance(v, str) and v.strip()) for v in code_from_llm.values()
      )

            if has_llm_code:
               row["code"] = code_from_llm
               # normalize import path if needed (ts -> js), optional
               for k in ("imports", "alt_handler_wrap", "hook", "jsx_attrs"):
                   if isinstance(row["code"].get(k), str):
                      row["code"][k] = row["code"][k].replace("../analytics/track.ts", "../analytics/track.js")
            else:
                analytics_id = _slug(item.get("adobe_value") or item.get("description") or "ui_element")[:64]

                if _HAS_SUGGESTER:
                    # Pass the augmented params/event name to the suggester by overriding on expl
                    expl_for_code = dict(expl or {})
                    expl_for_code["suggested_params"] = params
                    expl_for_code["suggested_event_name"] = event_name

                    if action in {"click", "select", "back", "exit", "nav"}:
                        row["code"] = suggest_click_like_code(item, expl_for_code)
                    elif action == "view":
                        row["code"] = suggest_view_code(item, expl_for_code)
                    else:
                        row["code"] = _fallback_click_code(event_name, params, analytics_id)
                else:
                   if action == "view":
                      row["code"] = _fallback_view_code(event_name, params)
                   else:
                      row["code"] = _fallback_click_code(event_name, params, analytics_id)


        else:
            row["top_match"] = None

        unified["items"].append(row)

    return unified


def write_outputs(unified: Dict[str, Any], out_dir: str = "outputs") -> Dict[str, str]:
    out = Path(out_dir)
    out.mkdir(exist_ok=True)

    json_path = out / "tagging_unified.json"
    md_path   = out / "tagging_unified.md"

    FileHandler.save_json(unified, str(json_path))
    md = to_markdown(unified)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # No JS module emitted
    return {
        "json": str(json_path.resolve()),
        "md": str(md_path.resolve()),
    }
