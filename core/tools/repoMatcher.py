# tools/repo_handler.py
from __future__ import annotations

import re
import math
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np
from langchain.tools import BaseTool

from utils.file_handler import FileHandler
from .openai_utils import embed_texts  # OpenAI embeddings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

JS_EVENT_HINTS = ["onClick", "onSubmit", "onChange", "onSelect", "onPress"]
JSX_TAG_HINTS  = ["<Button", "<button", "<Link", "<a ", "<IconButton", "<Touchable", "<Pressable"]

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

class RepoMatcherTool(BaseTool):
    """
    Given a React repo and normalized spec_items (from ExcelReaderTool),
    propose likely tagging locations.

    _run(repo_path: str, spec_items: List[Dict], use_embeddings: bool = True)
    """
    name = "repo_matcher"
    description = "Scans a React repo and proposes tagging locations (keyword + optional OpenAI embeddings)."

    def _run(self, repo_path: str, spec_items: List[Dict[str, Any]], use_embeddings: bool = True) -> Dict[str, Any]:
        try:
            files = FileHandler.find_react_files(repo_path)
            # pre-read contents
            contents: Dict[str, List[str]] = {f: FileHandler.read_file_content(f).splitlines() for f in files}

            # build a light index of candidate lines to keep embedding cost low
            candidates = self._collect_candidates(contents, spec_items)

            suggestions = []
            for idx, item in enumerate(spec_items):
                matches = self._score_candidates_for_item(item, candidates, use_embeddings=use_embeddings)
                suggestions.append({
                    "item_index": idx,
                    "sheet": item.get("sheet"),
                    "row_index": item.get("row_index"),
                    "description": item.get("description"),
                    "component": item.get("component"),
                    "action": item.get("action"),
                    "page": item.get("page"),
                    "adobe_var": item.get("adobe_var"),
                    "adobe_value": item.get("adobe_value"),
                    "target_terms": item.get("target_terms", []),
                    "matches": matches,
                })

            return {
                "status": "success",
                "repo": str(Path(repo_path).resolve()),
                "suggestions": suggestions,
                "summary": {
                    "items": len(spec_items),
                    "suggested": sum(1 for s in suggestions if s.get("matches")),
                    "embeddings_used": bool(use_embeddings),
                },
            }

        except Exception as e:
            logger.exception(f"RepoMatcherTool failed: {e}")
            return {"status": "error", "error": str(e)}

    # ---------- candidate collection ----------

    def _collect_candidates(self, contents: Dict[str, List[str]], spec_items: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, int, str]]]:
        """
        Return dict: {item_id: [(file, line_no, window_text), ...]}
        where window_text is ~16-line context around the hit.
        """
        term_sets = {i: [t.lower() for t in (item.get("target_terms") or [])] for i, item in enumerate(spec_items)}
        out: Dict[str, List[Tuple[str, int, str]]] = {}

        for i, terms in term_sets.items():
            out[str(i)] = []
            if not terms:
                continue

            for file, lines in contents.items():
                for ln, line in enumerate(lines, start=1):
                    low = line.lower()
                    if not any(t for t in terms if t and t in low):
                        continue
                    # take a small window around the hit for more semantic info
                    w = lines[max(1, ln - 8) - 1 : min(len(lines), ln + 8)]
                    window = "\n".join(w)
                    out[str(i)].append((file, ln, window))

            # soft fallback: if no keyword hits, still capture common interactive regions
            if not out[str(i)]:
                for file, lines in contents.items():
                    for ln, line in enumerate(lines, start=1):
                        if any(h in line for h in JS_EVENT_HINTS):
                            w = lines[max(1, ln - 4) - 1 : min(len(lines), ln + 6)]
                            out[str(i)].append((file, ln, "\n".join(w)))
                            if len(out[str(i)]) >= 30:
                                break
                    if len(out[str(i)]) >= 30:
                        break

        return out

    # ---------- scoring ----------

    def _score_candidates_for_item(self, item: Dict[str, Any], candidates: Dict[str, List[Tuple[str, int, str]]], use_embeddings: bool) -> List[Dict[str, Any]]:
        cid = str(item.get("item_index", item.get("row_index", "")))  # tolerate either
        cands = candidates.get(str(item.get("item_index")) or cid, [])
        if not cands:
            return []

        # base score from heuristics; then (optionally) semantic boost via embeddings
        scored: List[Dict[str, Any]] = []

        # Prepare query text
        q_terms = item.get("target_terms", [])
        q = f"page:{item.get('page') or ''} action:{item.get('action') or ''} desc:{item.get('description') or ''} terms:{', '.join(q_terms)}"

        if use_embeddings:
            # Embed query + all candidate windows
            texts = [q] + [win for (_, _, win) in cands]
            vecs = embed_texts(texts)  # [q_vec, cand1, cand2, ...]
            if not vecs:
                use_embeddings = False
            else:
                q_vec = np.array(vecs[0], dtype=np.float32)
                cand_vecs = [np.array(v, dtype=np.float32) for v in vecs[1:]]
        else:
            q_vec, cand_vecs = None, []

        for idx, (file, line_no, window) in enumerate(cands):
            # heuristic base
            base = 0.55
            if any(h in window for h in JS_EVENT_HINTS):
                base += 0.20
            if any(t in window for t in JSX_TAG_HINTS):
                base += 0.10
            if (item.get("action") == "view") and re.search(r"(Page|Screen|Route)", Path(file).name):
                base += 0.05

            sim = 0.0
            if use_embeddings and q_vec is not None:
                sim = _cosine(q_vec, cand_vecs[idx])
                # map cosine [-1,1] to [0, 0.25] boost (typical cos in [0.7, 0.95])
                boost = max(0.0, min(0.25, (sim - 0.5) * 0.5))
                base += boost

            conf = round(min(0.95, base), 2)
            evidence = []
            if any(h in window for h in JS_EVENT_HINTS):
                evidence.append("nearby event handler")
            if any(t in window for t in JSX_TAG_HINTS):
                evidence.append("clickable JSX element")
            if sim:
                evidence.append(f"semantic_sim={sim:.3f}")

            scored.append({
                "file": file,
                "line": line_no,
                "confidence": conf,
                "evidence": evidence,
            })

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored[:5]
