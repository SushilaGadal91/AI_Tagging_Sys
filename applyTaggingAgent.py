# tools/ai_repo_applier.py
from __future__ import annotations

import os
import re
import json
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Reuse your OpenAI utility (modern/legacy friendly)
try:
    from tools.openai_utils import get_client  # your helper
except Exception:
    raise RuntimeError("tools.openai_utils.get_client not found. Make sure your project structure matches.")

# ----------------- Markdown parsing (dynamic & robust) -----------------

MD_LOC_RE = re.compile(
    r"-\s+\*\*Suggested Location\*\*:\s*`(?P<file>[^`]+?):(?P<line>\d+)`",
    re.IGNORECASE,
)
MD_ACTION_RE = re.compile(r"-\s+\*\*Action\*\*:\s*`(?P<action>[^`]+)`", re.IGNORECASE)
MD_EVENT_RE  = re.compile(r"-\s+\*\*Event\*\*:\s*`(?P<event>[^`]+)`", re.IGNORECASE)
MD_PARAMS_START_RE = re.compile(r"-\s+\*\*Params:\*\*\s*$", re.IGNORECASE)

H3_KPI_RE = re.compile(r"^\s*###\s+KPI:", re.IGNORECASE)
H2_PAGE_RE = re.compile(r"^\s*##\s+Page:", re.IGNORECASE)

# Any italic underscore title like "_Hook:_", "_JSX attributes:_", "_My Custom Patch:_"
TITLE_ANY_RE = re.compile(r"^_+\s*(?P<title>[^:]+):_?\s*$", re.IGNORECASE)

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _write_text(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="")

def _find_fenced_block(lines: List[str], start_idx: int) -> Tuple[str, int, str]:
    """
    Return (code, next_index, lang) for a fenced block starting at or after start_idx.
    Supports ``` and language fences like ```jsx.
    Returns ("", idx, "") if not found.
    """
    i = start_idx
    while i < len(lines):
        ls = lines[i].lstrip()
        if ls.startswith("```"):
            fence = "```"
            lang = ls[3:].strip().lower()
            i += 1
            buf: List[str] = []
            while i < len(lines) and not lines[i].strip().startswith(fence):
                buf.append(lines[i].rstrip("\n"))
                i += 1
            return ("\n".join(buf).rstrip(), min(i + 1, len(lines)), lang)
        i += 1
    return ("", start_idx, "")

def _slug(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")

def _canonical_key(slug: str) -> str:
    if "import" in slug:
        return "imports"
    if "hook" in slug or "effect" in slug:
        return "hook"
    if "jsx" in slug or "attr" in slug:
        return "jsx_attrs"
    if "wrap" in slug or "handler" in slug:
        return "alt_handler_wrap"
    return slug  # dynamic passthrough

def parse_md_plan(md_path: Path) -> List[Dict[str, Any]]:
    """
    Parse tagging_unified.md -> list of items:
    { file, line, action, event, params, snippet, code:{... arbitrary keys ...} }
    Only items with a Suggested Location are included.
    """
    text = _read_text(md_path)
    lines = text.splitlines()
    items: List[Dict[str, Any]] = []

    i = 0
    while i < len(lines):
        if H3_KPI_RE.match(lines[i] or ""):
            rec: Dict[str, Any] = {"code": {}}
            pending_snippet: Optional[str] = None
            j = i + 1
            while j < len(lines) and not H3_KPI_RE.match(lines[j] or ""):
                if H2_PAGE_RE.match(lines[j] or "") and rec.get("file"):
                    break

                m = MD_ACTION_RE.search(lines[j]);      rec["action"] = (m.group("action").strip().lower() if m else rec.get("action"))
                m = MD_LOC_RE.search(lines[j])
                if m:
                    rec["file"] = m.group("file").strip()
                    try:
                        rec["line"] = int(m.group("line"))
                    except Exception:
                        rec["line"] = 1
                m = MD_EVENT_RE.search(lines[j]);       rec["event"] = (m.group("event").strip() if m else rec.get("event"))

                # Params block
                if MD_PARAMS_START_RE.match(lines[j] or ""):
                    code, j2, _ = _find_fenced_block(lines, j + 1)
                    try:
                        rec["params"] = json.loads(code) if code else {}
                    except Exception:
                        rec["params"] = {}
                    j = j2
                    continue

                # Snippet block (the code window from the repo)
                if lines[j].strip().startswith("```"):
                    code, j2, lang = _find_fenced_block(lines, j)
                    # keep the last JSX/TSX/JS snippet seen before "Suggested code to add" as the anchor snippet
                    if lang in {"jsx", "tsx", "js"} and code:
                        pending_snippet = code
                    j = j2
                    continue

                # Dynamic capture of any italic section under "Suggested code to add"
                if lines[j].strip().lower().startswith("**suggested code to add:**"):
                    if pending_snippet:
                        rec["snippet"] = pending_snippet
                    k = j + 1
                    while k < len(lines) and not (H3_KPI_RE.match(lines[k] or "") or H2_PAGE_RE.match(lines[k] or "")):
                        mtitle = TITLE_ANY_RE.match(lines[k].strip())
                        if mtitle:
                            slug = _slug(mtitle.group("title"))
                            key = _canonical_key(slug)
                            code, k, _ = _find_fenced_block(lines, k + 1)
                            rec["code"][key] = code
                            continue
                        k += 1
                    j = k
                    continue
                j += 1

            if rec.get("file"):
                items.append(rec)
            i = j
            continue
        i += 1

    return items

# ----------------- Utilities: fuzzy anchor via snippet -----------------

def _best_anchor_from_snippet(file_text: str, snippet: str) -> Optional[int]:
    """
    Fuzzy-locate the snippet in file_text and return a 1-based anchor line
    (middle of the matched block). Returns None if not found.
    """
    file_lines = file_text.splitlines()
    snip_lines = [ln for ln in snippet.splitlines() if ln.strip()]
    if not snip_lines or not file_lines:
        return None

    # Create a sliding window and pick the highest ratio match
    best_score = 0.0
    best_start = None
    window = min(len(file_lines), max(5, len(snip_lines)))
    for start in range(0, len(file_lines) - len(snip_lines) + 1):
        chunk = "\n".join(file_lines[start:start+len(snip_lines)])
        score = difflib.SequenceMatcher(None, chunk, "\n".join(snip_lines)).ratio()
        if score > best_score:
            best_score = score
            best_start = start

    if best_start is not None and best_score >= 0.6:  # threshold
        mid = best_start + (len(snip_lines) // 2)
        return max(1, min(len(file_lines), mid + 1))
    return None

# ----------------- LLM JSON extractor -----------------

def _extract_json(text: str) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("```")
    if start != -1:
        end = text.find("```", start + 3)
        if end != -1:
            body = text[start + 3:end]
            if "\n" in body:
                body = body.split("\n", 1)[1]
            try:
                return json.loads(body.strip())
            except Exception:
                pass
    # brace counting
    s = text; n = len(s); i = 0
    while i < n:
        if s[i] == "{":
            depth = 0; j = i
            while j < n:
                ch = s[j]
                if ch == "{": depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        cand = s[i:j+1]
                        try: return json.loads(cand)
                        except Exception: break
                j += 1
        i += 1
    return {}

# ----------------- Dynamic, TechSpec-driven prompt -----------------

CONFIG = {
    "language": "js",  # keep JS only
    "analytics_vendor": "adobe",
    "helper_import": "import { track } from '../analytics/track.js';",
}

DYNAMIC_SYSTEM = (
    "You are a careful code transformation assistant.\n"
    "Input:\n"
    " • Full text of a React **JavaScript** file (no TypeScript).\n"
    " • An anchor **line number** and a code **snippet** from the file near where tagging should be applied.\n"
    " • A tagging instruction for **Adobe Analytics** using a helper `track(eventName, params)`.\n"
    " • A dict of **code sections** extracted from a Tech Spec/MD (arbitrary keys).\n"
    "\n"
    "Rules (must follow):\n"
    " 1) JavaScript only. Preserve imports/eslint/comments/formatting as much as practical.\n"
    " 2) Idempotent: if the same tagging already exists, return the file unchanged with reason.\n"
    " 3) Edit at the JSX/component location that best matches BOTH the anchor number and the provided snippet.\n"
    " 4) Use provided **code sections** exactly where possible:\n"
    "    • Keys containing 'import'  → ensure these import lines exist once (augment existing imports).\n"
    "    • Keys containing 'hook'/'effect' → place inside component body, after declaration (page view).\n"
    "    • Keys containing 'attr'/'jsx' → merge into opening JSX tag at/near the anchor (click/select/back/etc.).\n"
    "    • Keys containing 'wrap'/'handler' → wrap or replace existing handler while preserving original behavior.\n"
    "    • Any **other** keys are treated as **patch snippets**: insert the snippet in a minimal, sensible location near the anchor.\n"
    " 5) If there is an existing handler (e.g., `onClick={handle}`), inject `track(...)` at the start and keep original logic.\n"
    " 6) Ensure **imports** are added once: {helper_import}\n"
    " 7) Do **not** invent code if a section is missing; only apply what is provided.\n"
    " 8) Output ONLY strict JSON: "
    "{ \"applied\": true|false, \"reason\": \"...\", \"updated_file\": \"<full text>\" }"
)

def _lines_context(file_text: str, line: int, radius: int = 40) -> str:
    lines = file_text.splitlines()
    if line < 1: line = 1
    if line > len(lines): line = len(lines)
    i0 = max(1, line - radius)
    i1 = min(len(lines), line + radius)
    chunk = lines[i0-1:i1]
    return "\n".join(f"{i0+idx:>5}: {ln}" for idx, ln in enumerate(chunk))

def _build_messages(
    file_text: str,
    action: str,
    event: str,
    params: Dict[str, Any],
    anchor_line: int,
    code: Dict[str, str],
    snippet: Optional[str],
) -> List[Dict[str, str]]:
    system = DYNAMIC_SYSTEM.replace("{helper_import}", CONFIG["helper_import"])
    instr = {
        "action": action,
        "event": event,
        "params": params,
        "anchor_line": anchor_line,
        "snippet": snippet or "",
        "code_sections": {k: v for k, v in (code or {}).items() if isinstance(v, str) and v.strip()},
        "around_anchor": _lines_context(file_text, anchor_line, radius=40),
        "vendor": CONFIG["analytics_vendor"],
        "language": CONFIG["language"],
        "notes": [
            "Apply only what is provided; do not synthesize missing sections.",
            "If both attrs and a handler patch exist, prefer attrs merge and inject track(...) in handler.",
            "Keep JSX valid; do not convert to TypeScript.",
        ],
    }
    user = (
        "FILE:\n<<FILE_START>>\n" + file_text + "\n<<FILE_END>>\n\n"
        "INSTRUCTION:\n" + json.dumps(instr, ensure_ascii=False)
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

def _ai_edit_file(
    client,
    model: str,
    file_text: str,
    action: str,
    event: str,
    params: Dict[str, Any],
    anchor_line: int,
    code: Dict[str, str],
    snippet: Optional[str],
) -> Dict[str, Any]:
    messages = _build_messages(file_text, action, event, params, anchor_line, code, snippet)
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=messages,
        )
        txt = resp.choices[0].message.content or ""
        data = _extract_json(txt) or {}
        if not isinstance(data, dict):
            return {"applied": False, "reason": "non-dict LLM response", "updated_file": file_text}
        if "updated_file" not in data:
            data["updated_file"] = file_text
        if "applied" not in data:
            data["applied"] = (data["updated_file"] != file_text)
        if "reason" not in data:
            data["reason"] = "ok" if data["applied"] else "no changes or already applied"
        return data
    except Exception as e:
        return {"applied": False, "reason": f"LLM error: {e}", "updated_file": file_text}

# ----------------- Public API -----------------

def ai_apply_from_md(
    md_path: str | Path,
    repo_root: str | Path,
    model: str = "gpt-4o-mini",
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Read the Markdown plan, ask the LLM to perform the edits, and write files.
    Returns (ok_count, fail_count). Creates .taggingai.bak backups.
    """
    client = get_client()
    md = Path(md_path).resolve()
    repo = Path(repo_root).resolve()

    items = parse_md_plan(md)
    if not items:
        print(f"✗ No actionable items found in {md}")
        return (0, 0)

    # log file to understand not-applied cases
    logs: List[Dict[str, Any]] = []

    ok = fail = 0
    for it in items:
        rel = it["file"]
        target = Path(rel)
        if not target.is_absolute():
            target = (repo / target).resolve()

        if not target.exists():
            msg = f"File not found: {target}"
            print(f"✗ {msg}")
            logs.append({**it, "result": {"applied": False, "reason": msg}})
            fail += 1
            continue

        try:
            src = _read_text(target)
        except Exception as e:
            msg = f"Read failed: {target} ({e})"
            print(f"✗ {msg}")
            logs.append({**it, "result": {"applied": False, "reason": msg}})
            fail += 1
            continue

        action  = (it.get("action") or "").lower().strip()
        event   = (it.get("event") or "custom_event").strip()
        params  = it.get("params") or {}
        code    = it.get("code") or {}
        snippet = it.get("snippet")

        # Better anchor via snippet (if available)
        anchor = int(it.get("line") or 1)
        better = _best_anchor_from_snippet(src, snippet) if snippet else None
        if better:
            anchor = better

        # First attempt
        result1 = _ai_edit_file(client, model, src, action, event, params, anchor, code, snippet)
        new_src = result1.get("updated_file") or src
        applied = bool(result1.get("applied"))
        reason  = (result1.get("reason") or "").strip() or ("ok" if applied else "no changes")

        # Retry once with larger context if not applied and unchanged
        if not applied and new_src == src:
            # Expand context by tweaking the anchor a bit (±20 lines)
            alt_anchor = max(1, min(len(src.splitlines()), anchor + 20))
            result2 = _ai_edit_file(client, model, src, action, event, params, alt_anchor, code, snippet)
            new_src2 = result2.get("updated_file") or src
            applied2 = bool(result2.get("applied"))
            reason2  = (result2.get("reason") or "").strip() or ("ok" if applied2 else "no changes")

            if applied2 and new_src2 != src:
                applied = True
                new_src = new_src2
                reason = f"retry_ok: {reason2}"
                result1 = result2
            else:
                reason = f"not_applied: {reason}; retry: {reason2}"

        if not applied and new_src == src:
            print(f"• {target}: {reason}")
            logs.append({**it, "result": {"applied": False, "reason": reason}})
            ok += 1  # idempotent/no-change treated as OK to keep pipeline moving
            continue

        if dry_run:
            print(f"[DRY-RUN] Would update: {target} ({reason})")
            logs.append({**it, "result": {"applied": True, "reason": f"dry_run: {reason}"}})
            ok += 1
            continue

        try:
            backup = target.with_suffix(target.suffix + ".taggingai.bak")
            if not backup.exists():
                _write_text(backup, src)
            _write_text(target, new_src)
            print(f"✓ Updated: {target} ({reason})  (backup: {backup.name})")
            logs.append({**it, "result": {"applied": True, "reason": reason, "backup": str(backup)}})
            ok += 1
        except Exception as e:
            msg = f"Write failed: {target} ({e})"
            print(f"✗ {msg}")
            logs.append({**it, "result": {"applied": False, "reason": msg}})
            fail += 1

    # persist logs next to the md
    try:
        out_log = md.parent / "apply_log.json"
        _write_text(out_log, json.dumps(logs, indent=2, ensure_ascii=False))
    except Exception:
        pass

    return ok, fail

# ------------- Optional CLI -------------

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    ap = argparse.ArgumentParser(description="AI-applier: modify repo files based on tagging_unified.md")
    ap.add_argument("--md", default="outputs/tagging_unified.md")
    ap.add_argument("--repo", default=os.environ.get("REPO_PATH", "."))
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ok, fail = ai_apply_from_md(args.md, args.repo, model=args.model, dry_run=args.dry_run)
    print(f"\nResult: {ok} items processed, {fail} failed.")
