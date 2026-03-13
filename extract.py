#!/usr/bin/env python3
"""Extract password-protected zip files from contagiodump."""

import sys
import zipfile
import argparse
from pathlib import Path


def get_passwords(path: Path) -> list[str]:
    """Return list of passwords to try for a given zip filename."""
    stem = path.stem
    primary = "infected666" + stem[-1] if stem else "infected666"
    return [primary, "infected"]


def extract_zip(zip_path: Path, dest_dir: Path) -> tuple[bool, str | None]:
    """Try to extract zip_path into dest_dir. Returns (success, password_used)."""
    for pwd in get_passwords(zip_path):
        try:
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(path=dest_dir, pwd=pwd.encode())
            return True, pwd
        except (RuntimeError, zipfile.BadZipFile):
            continue
    return False, None


def main():
    parser = argparse.ArgumentParser(description="Extract contagiodump zip files.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing zip files (default: current directory)")
    args = parser.parse_args()

    base_dir = Path(args.directory).resolve()
    zip_files = sorted(base_dir.glob("*.zip"))

    if not zip_files:
        print(f"No zip files found in {base_dir}")
        sys.exit(0)

    print(f"Found {len(zip_files)} zip file(s) in {base_dir}\n")

    ok, failed = 0, 0
    for zip_path in zip_files:
        dest_dir = base_dir / zip_path.stem
        dest_dir.mkdir(exist_ok=True)

        success, pwd_used = extract_zip(zip_path, dest_dir)
        if success:
            print(f"  [OK]  {zip_path.name}  (password: {pwd_used})")
            ok += 1
        else:
            print(f"  [WARN] {zip_path.name}  — extraction failed, all passwords exhausted")
            failed += 1

    print(f"\nDone: {ok} extracted, {failed} failed.")


if __name__ == "__main__":
    main()
