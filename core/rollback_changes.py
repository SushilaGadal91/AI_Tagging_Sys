#!/usr/bin/env python3
"""
Rollback Changes Script
Restores React files from their .taggingai.bak backups and deletes the backups.

Requires .env with:
  REPO_PATH=/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js
"""

import os
import shutil
from pathlib import Path

# Load .env (if available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def main():
    print(" ROLLBACK CHANGES (restore + delete backups)")
    print("=" * 20)

    repo_root_str = os.getenv("REPO_PATH")
    if not repo_root_str:
        print(" REPO_PATH not set in .env")
        print("   Example: REPO_PATH=/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js")
        return

    repo_root = Path(repo_root_str).expanduser().resolve()
    src_path = (repo_root / "src").resolve()
    if not src_path.exists():
        print(" Could not find your src folder.")
        print(f"   Looked at: {src_path}")
        return

    print(f"Using repo src at: {src_path}")

    # Find backups (files only)
    backup_files = [p for p in src_path.rglob("*.taggingai.bak") if p.is_file()]
    if not backup_files:
        print(" No backup files found! Looked for: *.taggingai.bak")
        return

    print(f"Found {len(backup_files)} backup files")

    restored = deleted = 0
    SUFFIX = ".taggingai.bak"

    for backup in backup_files:
        # Compute original path: Foo.js.taggingai.bak -> Foo.js
        backup_str = str(backup)
        if not backup_str.endswith(SUFFIX):
            print(f" Skipping unexpected file: {backup}")
            continue
        original = Path(backup_str[:-len(SUFFIX)])

        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, original)
            print(f" Restored {original.relative_to(repo_root)}")
            restored += 1

            # Delete backup after successful restore
            backup.unlink()
            deleted += 1
            # print(f" Deleted backup {backup.relative_to(repo_root)}")
        except Exception as e:
            try:
                b_rel = backup.relative_to(repo_root)
            except Exception:
                b_rel = backup
            try:
                o_rel = original.relative_to(repo_root)
            except Exception:
                o_rel = original
            print(f"Failed {b_rel} → {o_rel}: {e}")

    print(f"\n Rollback complete! {restored}/{len(backup_files)} restored, {deleted} backups deleted")


if __name__ == "__main__":
    main()
