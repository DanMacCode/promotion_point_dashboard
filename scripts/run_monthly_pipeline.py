"""
run_monthly_pipeline.py

Runs the promotion point dashboard data pipeline from a clean slate.

What it does:
1) Deletes all files in:
   - data/pdfs
   - data/txt
   - data/csv
2) Deletes:
   - data/master/master_promotion_data.csv
3) Runs the pipeline in strict order, stopping on the first failure:
   - scrape_pdfs.py
   - pdf_to_txt.py
   - rename_txts.py
   - cleanup_oldtxts.py
   - txt_to_csv.py
   - compile_master_dataset.py

Usage:
  From the project root:
    python scripts/run_monthly_pipeline.py

Or from anywhere:
    python C:\Users\macle\Data_Projects\promotion_point_dashboard\scripts\run_monthly_pipeline.py
"""

import sys
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(r"C:\Users\macle\Data_Projects\promotion_point_dashboard").resolve()
DATA_DIR = PROJECT_ROOT / "data"

PDFS_DIR = DATA_DIR / "pdfs"
TXT_DIR = DATA_DIR / "txt"
CSV_DIR = DATA_DIR / "csv"
MASTER_FILE = DATA_DIR / "master" / "master_promotion_data.csv"

SCRIPTS_DIR = PROJECT_ROOT / "scripts"

PIPELINE = [
    "scrape_pdfs.py",
    "pdf_to_txt.py",
    "rename_txts.py",
    "cleanup_oldtxts.py",
    "txt_to_csv.py",
    "compile_master_dataset.py",
]


def delete_contents(folder: Path) -> None:
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return

    for p in folder.iterdir():
        try:
            if p.is_file() or p.is_symlink():
                p.unlink()
            elif p.is_dir():
                # Remove directory and its contents safely
                for child in p.rglob("*"):
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                # Remove empty dirs bottom-up
                for child_dir in sorted([d for d in p.rglob("*") if d.is_dir()], reverse=True):
                    child_dir.rmdir()
                p.rmdir()
        except Exception as e:
            raise RuntimeError(f"Failed to delete {p}: {e}") from e


def delete_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except Exception as e:
        raise RuntimeError(f"Failed to delete {path}: {e}") from e


def run_script(script_name: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Pipeline script not found: {script_path}")

    # This blocks until completion. If it fails, we stop.
    print(f"\n=== RUNNING: {script_name} ===")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        print(result.stdout)

    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr)
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")

    print(f"=== COMPLETE: {script_name} ===")


def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")

    # Safety checks
    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(f"PROJECT_ROOT does not exist: {PROJECT_ROOT}")
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"DATA_DIR does not exist: {DATA_DIR}")
    if not SCRIPTS_DIR.exists():
        raise FileNotFoundError(f"SCRIPTS_DIR does not exist: {SCRIPTS_DIR}")

    print("\n=== CLEANING DATA DIRECTORIES ===")
    for folder in [PDFS_DIR, TXT_DIR, CSV_DIR]:
        print(f"Clearing: {folder}")
        delete_contents(folder)

    print(f"Deleting master file: {MASTER_FILE}")
    delete_file(MASTER_FILE)

    print("\n=== STARTING PIPELINE ===")
    for script in PIPELINE:
        run_script(script)

    print("\n✅ Pipeline finished successfully.")


if __name__ == "__main__":
    main()