# tools/openai_utils.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional

# Try modern 1.x client first; fall back to legacy 0.x module API
try:
    from openai import OpenAI  # 1.x style
    _MODERN = True
except Exception:
    import openai as _openai   # 0.x style
    OpenAI = None
    _MODERN = False

_CLIENT = None

def get_client():
    """
    Return a client compatible with the installed SDK.
    - 1.x: OpenAI()
    - 0.x: openai module with api_key set
    """
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    if _MODERN:
        _CLIENT = OpenAI(api_key=api_key)
    else:
        _openai.api_key = api_key  # type: ignore[attr-defined]
        _CLIENT = _openai
    return _CLIENT


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Extract the first valid top-level JSON object from 'text' without regex recursion.
    Handles prose and fenced code blocks.
    """
    if not text:
        return {}

    # 1) Try direct parse (sometimes model returns pure JSON)
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) Look for a fenced ```json block
    start = text.find("```")
    if start != -1:
        end = text.find("```", start + 3)
        if end != -1:
            fenced = text[start + 3:end]
            # Drop optional language tag (e.g., "json\n")
            if "\n" in fenced:
                fenced = fenced.split("\n", 1)[1]
            fenced = fenced.strip()
            try:
                return json.loads(fenced)
            except Exception:
                pass

    # 3) Count braces to find first balanced {...}
    s = text
    n = len(s)
    i = 0
    while i < n:
        if s[i] == "{":
            depth = 0
            j = i
            while j < n:
                ch = s[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = s[i:j + 1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            # keep scanning for next balanced block
                            break
                j += 1
        i += 1

    return {}


def llm_json_infer(row_payload: Dict[str, Any], model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Normalize a tech-spec row into:
      { action, page, target_terms: [] }
    Uses chat.completions (no response_format) for compatibility across SDKs.
    """
    client = get_client()

    system_msg = (
        "You are a senior analytics implementation engineer. "
        "Given a Tech Spec row describing a UI element and analytics requirements, "
        "return ONLY a JSON object with fields: "
        "{action, page, target_terms}. "
        "action ∈ {click, submit, view, back, exit, select, nav, general}. "
        "page is a short page/screen name if obvious. "
        "target_terms is a short list (1–4) of literal UI phrases users see/click. "
        "No explanations."
        "Suggest the code changes needed to implement the tagging. "
    )
    user_msg = json.dumps(row_payload, ensure_ascii=False)

    if _MODERN:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )
            text = resp.choices[0].message.content or ""
            data = _extract_json(text)
            return {
                "action": data.get("action"),
                "page": data.get("page"),
                "target_terms": data.get("target_terms") or [],
            }
        except Exception:
            return {"action": None, "page": None, "target_terms": []}
    else:
        try:
            resp = client.ChatCompletion.create(  # type: ignore[attr-defined]
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )
            text = resp["choices"][0]["message"]["content"]
            data = _extract_json(text)
            return {
                "action": data.get("action"),
                "page": data.get("page"),
                "target_terms": data.get("target_terms") or [],
            }
        except Exception:
            return {"action": None, "page": None, "target_terms": []}


def embed_texts(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """
    Return embeddings for texts. Handles both 1.x and 0.x SDKs.
    """
    if not texts:
        return []
    client = get_client()

    if _MODERN:
        res = client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in res.data]
    else:
        res = client.Embedding.create(model=model, input=texts)  # type: ignore[attr-defined]
        return [d["embedding"] for d in res["data"]]


def llm_explain_mapping(
    spec_item: dict,
    top_match: dict,
    code_context: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Explain KPI -> code location and propose event details **with code**:
      returns {
        kpi, why_location, suggested_event_name, suggested_params, implementation_note, risks,
        code: { imports?, jsx_attrs?, alt_handler_wrap?, hook? }
      }
    """
    client = get_client()

    # >>> UPDATED PROMPT: requires a structured "code" object <<<
    system_msg = (
       "You are a senior analytics implementation engineer. "
       "The analytics stack is **Adobe Analytics (AppMeasurement/Launch)**. "
       "Given a KPI row from a Tech Spec and the best-matched code location in a React repo, "
       "return ONLY a JSON object with fields: "
       "{kpi, why_location, suggested_event_name, suggested_params, implementation_note, risks, code}. "
       "'suggested_params' must be a flat JSON object and, when applicable, MUST include Adobe keys like "
       "eVarXX/propXX (e.g., eVar10) with the value from the tech spec, and may include 'events' (e.g., 'event12'). "
       "For **page views**, include a boolean flag '__pv': true and, if known, 'pageName'. "
       "'risks' must be an ARRAY OF SHORT STRINGS. "
       "'code' must be an object that may include any of these string fields (omit if N/A): "
       "  - imports (JavaScript import lines; no backticks), "
       "  - jsx_attrs (JSX attributes for a clickable element; no backticks), "
       "  - alt_handler_wrap (wrapper if an existing onClick must be preserved; no backticks), "
       "  - hook (a React useEffect snippet for page view; no backticks). "
       "All code MUST be plain JavaScript (no TypeScript types) and should call a helper `track(eventName, params)` "
       "Always import the helper exactly as: import { track } from '../analytics/track.js'; "
       "Do not use any other path (no ./analytics, ../analytics/index, missing extension, or barrel files)."
       "Never add this import inside src/analytics/track.js itself (avoid self-import)."
       "that is implemented for Adobe (internally uses s.t / s.tl, linkTrackVars, linkTrackEvents, clearVars). "
       "Keep answers concise and actionable. Only return a JSON object; do not include code fences or prose."
    )

    user_payload = {
        "spec_item": {
            "page": spec_item.get("page"),
            "action": spec_item.get("action"),
            "description": spec_item.get("description"),
            "adobe_var": spec_item.get("adobe_var"),
            "adobe_value": spec_item.get("adobe_value"),
            "target_terms": spec_item.get("target_terms"),
        },
        "top_match": {
            "file": top_match.get("file"),
            "line": top_match.get("line"),
            "confidence": top_match.get("confidence"),
            "evidence": top_match.get("evidence"),
        },
        "code_context": code_context,  # nearby lines to help the model shape the snippet
    }
    user_msg = json.dumps(user_payload, ensure_ascii=False)

    if _MODERN:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )
            text = resp.choices[0].message.content or ""
            data = _extract_json(text)
            return {
                "kpi": data.get("kpi") or spec_item.get("description"),
                "why_location": data.get("why_location"),
                "suggested_event_name": data.get("suggested_event_name"),
                "suggested_params": data.get("suggested_params") or {},
                "implementation_note": data.get("implementation_note"),
                "risks": data.get("risks") or [],
                # NEW: structured code (and keep your old key as a fallback if present)
                "code": data.get("code") or {},
                "suggested_code_changes": data.get("suggested_code_changes") or "",
            }
        except Exception:
            return {
                "kpi": spec_item.get("description"),
                "why_location": None,
                "suggested_event_name": None,
                "suggested_params": {},
                "implementation_note": None,
                "risks": [],
                "code": {},
                "suggested_code_changes": "",
            }
    else:
        try:
            resp = client.ChatCompletion.create(  # type: ignore[attr-defined]
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0,
            )
            text = resp["choices"][0]["message"]["content"]
            data = _extract_json(text)
            return {
                "kpi": data.get("kpi") or spec_item.get("description"),
                "why_location": data.get("why_location"),
                "suggested_event_name": data.get("suggested_event_name"),
                "suggested_params": data.get("suggested_params") or {},
                "implementation_note": data.get("implementation_note"),
                "risks": data.get("risks") or [],
                "code": data.get("code") or {},
                "suggested_code_changes": data.get("suggested_code_changes") or "",
            }
        except Exception:
            return {
                "kpi": spec_item.get("description"),
                "why_location": None,
                "suggested_event_name": None,
                "suggested_params": {},
                "implementation_note": None,
                "risks": [],
                "code": {},
                "suggested_code_changes": "",
            }
