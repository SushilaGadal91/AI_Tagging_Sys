# tools/ai_repo_applier.py (JSON-driven)
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

# ----------------- Utilities -----------------

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _write_text(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="")

def to_posix(p: str) -> str:
    if not p:
        return p
    p2 = p.replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", p2)
    if m:
        return f"/mnt/{m.group(1).lower()}/{m.group(2)}"
    return p2

# ----------------- Fuzzy anchor via snippet -----------------

def _clean_numbered_snippet(snippet: str) -> str:
    lines = []
    for ln in (snippet or "").splitlines():
        # strip leading '  10: ' style prefixes
        lines.append(re.sub(r"^\s*\d+:\s?", "", ln))
    return "\n".join(lines).strip()


def _best_anchor_from_snippet(file_text: str, snippet: str) -> Optional[int]:
    """Fuzzy-locate the snippet in file_text and return a 1-based anchor line (middle of block)."""
    file_lines = file_text.splitlines()
    snip = _clean_numbered_snippet(snippet)
    snip_lines = [ln for ln in snip.splitlines() if ln.strip()]
    if not snip_lines or not file_lines:
        return None

    best_score = 0.0
    best_start = None
    for start in range(0, len(file_lines) - len(snip_lines) + 1):
        chunk = "\n".join(file_lines[start:start + len(snip_lines)])
        score = difflib.SequenceMatcher(None, chunk, "\n".join(snip_lines)).ratio()
        if score > best_score:
            best_score = score
            best_start = start

    if best_start is not None and best_score >= 0.6:
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
    # fenced
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
    # brace scan
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

# ----------------- Prompt config -----------------

CONFIG = {
    "language": "js",
    "analytics_vendor": "adobe",
    "helper_import": "import { track } from '../analytics/track.js';",
}

DYNAMIC_SYSTEM = (
    "You are a careful code transformation assistant.\n"
    "Input:\n"
    " • Full text of a React **JavaScript** file (no TypeScript).\n"
    " • An anchor **line number** and a code **snippet** from the file near where tagging should be applied.\n"
    " • A tagging instruction for **Adobe Analytics** using a helper `track(eventName, params)`.\n"
    " • A dict of **code sections** provided directly from a JSON spec (arbitrary keys).\n"
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
    " 6) Ensure a single import exists: {helper_import} (prefer named import).\n"
    " 7) If you add a hook that calls useEffect(...), you MUST also ensure useEffect is imported:\n"
    "       • Prefer augmenting an existing React import:  import React, { ..., useEffect } from 'react';\n"
    "       • Otherwise add:                               import { useEffect } from 'react';\n"
    " 8) Do not invent code if a section is missing; only apply what is provided.\n"
    " 9) Output ONLY strict JSON: "
    "{ \"applied\": true|false, \"reason\": \"...\", \"updated_file\": \"<full text>\" }"
)

# ----------------- Message building -----------------

def _lines_context(file_text: str, line: int, radius: int = 40) -> str:
    lines = file_text.splitlines()
    if line < 1: line = 1
    if line > len(lines): line = len(lines)
    i0 = max(1, line - radius)
    i1 = min(len(lines), line + radius)
    chunk = lines[i0-1:i1]
    return "\n".join(f"{i0+idx:>5}: {ln}" for idx, ln in enumerate(chunk))


def _normalize_import_line(s: str) -> str:
    s = s.strip()
    # convert default import to named import (matches helper export)
    s = re.sub(r"^import\s+track\s+from\s+", "import { track } from ", s)
    return s


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

    # normalize imports inside code sections (JSON might contain default import style)
    code_sections = {}
    for k, v in (code or {}).items():
        if isinstance(v, str) and v.strip():
            if "import" in k.lower():
                code_sections[k] = _normalize_import_line(v)
            else:
                code_sections[k] = v

    instr = {
        "action": action,
        "event": event,
        "params": params,
        "anchor_line": anchor_line,
        "snippet": _clean_numbered_snippet(snippet or ""),
        "code_sections": code_sections,
        "around_anchor": _lines_context(file_text, anchor_line, radius=40),
        "vendor": CONFIG["analytics_vendor"],
        "language": CONFIG["language"],
        "notes": [
            "Use named import for track.",
            "If both attrs and a handler patch exist, prefer attrs merge and inject track(...) in handler.",
            "Keep JSX valid; do not convert to TypeScript.",
        ],
    }

    user = (
        "FILE:\n<<FILE_START>>\n" + file_text + "\n<<FILE_END>>\n\n" +
        "INSTRUCTION:\n" + json.dumps(instr, ensure_ascii=False)
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

# ----------------- LLM edit -----------------

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

# ----------------- JSON parsing -----------------

def parse_json_plan(json_path: Path) -> Dict[str, Any]:
    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------- Public API -----------------

def ai_apply_from_json(
    json_path: str | Path,
    repo_root: str | Path,
    model: str = "gpt-4o-mini",
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Read the JSON spec (items[*]) and ask the LLM to perform the edits.
    Returns (ok_count, fail_count). Creates .taggingai.bak backups.
    """
    client = get_client()
    js = Path(json_path).resolve()
    repo = Path(to_posix(str(repo_root))).resolve()

    data = parse_json_plan(js)
    items = data.get("items") or data.get("suggestions") or []
    if not items:
        print(f"✗ No actionable items found in {js}")
        return (0, 0)

    # optional helper file creation
    helper = data.get("helper_file") or {}
    try:
        helper_path = helper.get("path")
        helper_contents = helper.get("contents")
        if helper_path and helper_contents is not None:
            hp = (repo / helper_path).resolve()
            hp.parent.mkdir(parents=True, exist_ok=True)
            if not hp.exists() or _read_text(hp) != helper_contents:
                _write_text(hp, helper_contents)
                print(f"🧩 Helper file updated: {hp}")
            else:
                print(f"🧩 Helper file already up-to-date: {hp}")
    except Exception as e:
        print(f"⚠️  Helper file update skipped: {e}")

    logs: List[Dict[str, Any]] = []
    ok = fail = 0

    for it in items:
        # Resolve target file
        file_hint = (
            (it.get("top_match") or {}).get("file")
            or it.get("file")
            or it.get("file_path")
        )
        if not file_hint:
            msg = "Missing file path in item"
            print(f"✗ {msg}")
            logs.append({**it, "result": {"applied": False, "reason": msg}})
            fail += 1
            continue

        target = Path(to_posix(file_hint))
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

        # Gather instruction fields
        action  = (it.get("action") or "").lower().strip()
        event   = (it.get("suggested_event_name") or it.get("event") or "custom_event").strip()
        params  = it.get("suggested_params") or it.get("params") or {}
        code    = it.get("code") or {}
        snippet = it.get("snippet")  # may include numbered lines

        # anchor: use provided top_match.line else fuzzy from snippet
        anchor = int((it.get("top_match") or {}).get("line") or 1)
        better = _best_anchor_from_snippet(src, snippet) if snippet else None
        if better:
            anchor = better

        # 1st attempt
        result1 = _ai_edit_file(client, model, src, action, event, params, anchor, code, snippet)
        new_src = result1.get("updated_file") or src
        applied = bool(result1.get("applied"))
        reason  = (result1.get("reason") or "").strip() or ("ok" if applied else "no changes")

        # Retry once with shifted anchor if unchanged
        if not applied and new_src == src:
            alt_anchor = max(1, min(len(src.splitlines()), anchor + 20))
            result2 = _ai_edit_file(client, model, src, action, event, params, alt_anchor, code, snippet)
            new_src2 = result2.get("updated_file") or src
            applied2 = bool(result2.get("applied"))
            reason2  = (result2.get("reason") or "").strip() or ("ok" if applied2 else "no changes")
            if applied2 and new_src2 != src:
                applied = True
                new_src = new_src2
                reason = f"retry_ok: {reason2}"
            else:
                reason = f"not_applied: {reason}; retry: {reason2}"

        if not applied and new_src == src:
            print(f"• {target}: {reason}")
            logs.append({**it, "result": {"applied": False, "reason": reason}})
            ok += 1  # treat idempotent/no-op as OK
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

    # persist logs next to the JSON
    try:
        out_log = js.parent / "apply_log.json"
        _write_text(out_log, json.dumps(logs, indent=2, ensure_ascii=False))
    except Exception:
        pass

    return ok, fail

# ------------- Optional CLI -------------

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    ap = argparse.ArgumentParser(description="AI-applier: modify repo files based on tagging_unified.json")
    ap.add_argument("--json", default="outputs/tagging_unified.json")
    ap.add_argument("--repo", default=os.environ.get("REPO_PATH", "."))
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ok, fail = ai_apply_from_json(args.json, args.repo, model=args.model, dry_run=args.dry_run)
    print(f"\nResult: {ok} items processed, {fail} failed.")