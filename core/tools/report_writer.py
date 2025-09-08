# tools/report_writer.py
from __future__ import annotations
import json
from typing import Dict, List

def take_window(lines: List[str], line_no: int, radius: int = 6) -> str:
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    chunk = lines[start-1:end]
    # add simple line numbers for readability
    return "\n".join(f"{i+start:>4}: {t}" for i, t in enumerate(chunk))

# ---------- helpers to render code sections safely ----------

def _text_or_none(val: object) -> str:
    """Return a safe string for any value (no crashes)."""
    if val is None:
        return "// (none)"
    if isinstance(val, str):
        s = val.strip()
        return s if s else "// (none)"
    if isinstance(val, (dict, list)):
        try:
            return json.dumps(val, indent=2, ensure_ascii=False)
        except Exception:
            return str(val)
    return str(val).strip() or "// (none)"

def _is_js_event(attr_name: str) -> bool:
    # e.g., onClick, onChange, onSubmit
    return attr_name.startswith("on") and len(attr_name) > 2 and attr_name[2].isupper()

def _fmt_jsx_attrs(val: object) -> str:
    """
    Render JSX attributes. If dict → convert to lines like key="..." or key={...}.
    If string → trim. Else → stringify.
    """
    if val is None:
        return "// (none)"
    if isinstance(val, str):
        return val.strip() or "// (none)"
    if not isinstance(val, dict):
        return _text_or_none(val)

    lines: List[str] = []
    for k, v in val.items():
        if isinstance(v, str):
            vv = v.strip()
            if _is_js_event(k):
                # handlers should be expressions
                if vv.startswith("{") and vv.endswith("}"):
                    lines.append(f"{k}={vv}")
                else:
                    lines.append(f"{k}={{ {vv} }}")
            else:
                # plain attribute; preserve {expr} if provided, else quote
                if vv.startswith("{") and vv.endswith("}"):
                    lines.append(f"{k}={vv}")
                else:
                    vvq = vv.replace('"', '\\"')
                    lines.append(f'{k}="{vvq}"')
        else:
            try:
                vv = json.dumps(v, ensure_ascii=False)
            except Exception:
                vv = str(v)
            lines.append(f"{k}={{ {vv} }}")
    return ("\n".join(lines)).strip() or "// (none)"

# ------------------------------------------------------------

def to_markdown(unified: Dict) -> str:
    out: List[str] = []
    out.append(f"# Tagging Suggestions Report\n")
    out.append(f"- **Excel**: `{unified.get('excel')}`")
    out.append(f"- **Repo**: `{unified.get('repo')}`")
    out.append(f"- **Items**: {len(unified.get('items', []))}")
    out.append("")

    # Group by page for readability
    items = sorted(unified.get("items", []), key=lambda x: (x.get("page") or "", x.get("kpi") or ""))
    current_page = None
    for it in items:
        page = it.get("page") or "General"
        if page != current_page:
            out.append(f"## Page: {page}")
            current_page = page

        out.append(f"### KPI: {it.get('kpi')}")
        out.append(f"- **Action**: `{it.get('action')}`")

        if it.get("adobe"):
            out.append(f"- **Adobe**: var=`{it['adobe'].get('var')}`, value=`{it['adobe'].get('value')}`")

        if it.get("top_match"):
            tm = it["top_match"]
            out.append(f"- **Suggested Location**: `{tm.get('file')}:{tm.get('line')}`  (confidence {tm.get('confidence')})")

            if it.get("why_location"):
                out.append(f"- **Why here**: {it.get('why_location')}")

            if it.get("suggested_event_name"):
                out.append(f"- **Event**: `{it.get('suggested_event_name')}`")

            # Show params as pretty JSON (if present)
            if it.get("suggested_params"):
                try:
                    params_json = json.dumps(it.get("suggested_params"), indent=2, ensure_ascii=False)
                    out.append("- **Params:**")
                    out.append("```json")
                    out.append(params_json)
                    out.append("```")
                except Exception:
                    out.append(f"- **Params**: `{it.get('suggested_params')}`")

            if it.get("implementation_note"):
                out.append(f"- **Implementation**: {it.get('implementation_note')}")

            if it.get("risks"):
                out.append(f"- **Risks**: {', '.join(it.get('risks'))}")

            # Surrounding code where we'll tag
            if it.get("snippet"):
                out.append("\n```jsx")
                out.append(it["snippet"])
                out.append("```\n")

            # === paste-ready code suggestions (JavaScript / JSX) ===
            code = it.get("code")
            if code:
                out.append("**Suggested code to add:**")

                imports_str = _text_or_none(code.get("imports"))
                hook_str    = _text_or_none(code.get("hook"))
                attrs_str   = _fmt_jsx_attrs(code.get("jsx_attrs"))
                wrap_str    = _text_or_none(code.get("alt_handler_wrap"))

                if code.get("imports") is not None:
                    out.append("\n_Imports (add once per file if missing):_")
                    out.append("```js")
                    out.append(imports_str)
                    out.append("```")

                if code.get("hook") is not None:
                    out.append("\n_Hook (page view):_")
                    out.append("```jsx")
                    out.append(hook_str)
                    out.append("```")

                if code.get("jsx_attrs") is not None:
                    out.append("\n_JSX attributes (apply to the element):_")
                    out.append("```jsx")
                    out.append("<YourElement")
                    out.append(attrs_str)
                    out.append(">")
                    out.append("  ...")
                    out.append("</YourElement>")
                    out.append("```")

                if code.get("alt_handler_wrap") is not None:
                    out.append("\n_Alternative wrapper (if preserving existing handler):_")
                    out.append("```js")
                    out.append(wrap_str)
                    out.append("```")

        else:
            out.append("- **Suggested Location**: *(none found — search terms may be missing in UI)*\n")

    # Optional helper file section (only if agent provided it)
    helper = unified.get("helper_file")
    if helper and helper.get("path") and helper.get("contents"):
        out.append("\n---\n")
        out.append("## Optional analytics helper")
        out.append(f"_Create `{helper.get('path')}` if you don't already have a tracking util:_")
        out.append("```js")
        out.append(_text_or_none(helper.get("contents")))
        out.append("```")

    return "\n".join(out)

def to_js_module(unified: Dict) -> str:
    """Return an ES module that exports the unified tagging object (including code strings)."""
    obj = json.dumps(unified, indent=2, ensure_ascii=False)
    return (
        "// Auto-generated tagging plan with code suggestions (JS)\n"
        "// Do not edit by hand\n\n"
        f"export const taggingUnified = {obj};\n"
        "export default taggingUnified;\n"
    )
