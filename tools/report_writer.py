# tools/report_writer.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

def take_window(lines: List[str], line_no: int, radius: int = 6) -> str:
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    chunk = lines[start-1:end]
    # add simple line numbers for readability
    return "\n".join(f"{i+start:>4}: {t}" for i, t in enumerate(chunk))

def to_markdown(unified: Dict) -> str:
    out = []
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

            # Show the surrounding code where we'll tag
            if it.get("snippet"):
                out.append("\n```jsx")
                out.append(it["snippet"])
                out.append("```\n")

            # === NEW: paste-ready code suggestions (JavaScript / JSX) ===
            code = it.get("code")
            if code:
                out.append("**Suggested code to add:**")

                if code.get("imports"):
                    out.append("\n_Imports (add once per file if missing):_")
                    out.append("```js")
                    out.append(code["imports"].rstrip())
                    out.append("```")

                if code.get("hook"):
                    out.append("\n_Hook (page view):_")
                    out.append("```jsx")
                    out.append(code["hook"].rstrip())
                    out.append("```")

                if code.get("jsx_attrs"):
                    out.append("\n_JSX attributes (apply to the element):_")
                    out.append("```jsx")
                    out.append("<YourElement")
                    out.append(code["jsx_attrs"].rstrip())
                    out.append(">")
                    out.append("  ...")
                    out.append("</YourElement>")
                    out.append("```")

                if code.get("alt_handler_wrap"):
                    out.append("\n_Alternative wrapper (if preserving existing handler):_")
                    out.append("```js")
                    out.append(code["alt_handler_wrap"].rstrip())
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
        out.append(helper.get("contents", "").rstrip())
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
