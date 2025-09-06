# quick_start.py
import os
import sys
import time
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv

from agents.agent import build_unified, write_outputs

# ---------- tiny CLI UI helpers ----------
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

class Spinner:
    def __init__(self, label: str):
        self.label = label
        self._running = False

    def start(self):
        self._running = True
        self._animate_start = time.perf_counter()
        i = 0
        while self._running:
            frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
            sys.stdout.write(f"\r{frame} {self.label} ")
            sys.stdout.flush()
            i += 1
            time.sleep(0.08)

    def stop(self, ok: bool = True):
        self._running = False
        elapsed = time.perf_counter() - self._animate_start
        icon = "✓" if ok else "✗"
        sys.stdout.write(f"\r{icon} {self.label}  ({elapsed:.1f}s)\n")
        sys.stdout.flush()

@contextmanager
def step(label: str):
    sp = Spinner(label)
    try:
        import threading
        t = threading.Thread(target=sp.start, daemon=True)
        t.start()
        yield sp
        sp.stop(ok=True)
    except Exception:
        sp.stop(ok=False)
        raise

# ---------- main ----------
def main():
    load_dotenv()
    use_llm = bool(os.getenv("OPENAI_API_KEY"))

    # Resolve inputs
    excel_candidates = [
        os.getenv("TECHSPEC_PATH")
        # "TechSpec_Tagging.xlsx",
        # "techspec.xlsx",
    ]
    excel = next((p for p in excel_candidates if p and Path(p).exists()), None)
    if not excel:
        print("✗ Could not find a Tech Spec Excel file. Looked for:")
        for c in excel_candidates:
            if c:
                print(f"  - {c}")
        sys.exit(1)

    repo = os.getenv("REPO_PATH")
    if not Path(repo).exists():
        print(f"✗ React repo not found at: {repo}")
        sys.exit(1)

    print("==========================================")
    print(" Agentic Tagging — Unified Suggestions Run ")
    print("==========================================")
    print(f"• Tech Spec : {excel}")
    print(f"• Repo      : {repo}")
    print(f"• OpenAI    : {'ON (LLM + embeddings)' if use_llm else 'OFF (heuristics only)'}")
    print("")

    # Build unified output (parsing spec, scanning repo, mapping, LLM reasoning)
    with step("Analyzing Tech Spec + Scanning Repo + Generating Suggestions"):
        unified = build_unified(excel, repo, use_llm=use_llm)

    # Write files
    with step("Writing outputs (JSON / Markdown / JS module if enabled)"):
        out = write_outputs(unified)

    # Summary
    items = len(unified.get("items", []))
    suggested = sum(1 for it in unified.get("items", []) if it.get("top_match"))
    print("")
    print("Summary")
    print("-------")
    print(f"• Items processed : {items}")
    print(f"• With suggestions: {suggested}/{items}")
    print("")
    print("Outputs")
    print("-------")
    print(f"• JSON     : {out.get('json')}")
    print(f"• Markdown : {out.get('md')}")
    if out.get("js"):
        print(f"• JS module: {out.get('js')}")
    print("")

    print("Done ✅")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
    except Exception as e:
        # Show a concise error with a hint to enable verbose logs
        print(f"\n✗ Error: {e}")
        print("Hint: set more logs in your modules or run with environment-specific debug flags.")
        raise
