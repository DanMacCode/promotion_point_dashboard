"""
run_monthly_pipeline.py

Runs the promotion point dashboard data pipeline from a clean slate.

Steps
1) Delete all files in data/pdfs, data/txt, data/csv
2) Delete data/master/master_promotion_data.csv
3) Run scripts in strict order and stop on first failure
"""

import sys
import subprocess
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
    folder.mkdir(parents=True, exist_ok=True)
    for p in folder.iterdir():
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
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

    print(f"\nRUNNING {script_name}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")

    print(f"COMPLETE {script_name}")


def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")

    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(f"PROJECT_ROOT does not exist: {PROJECT_ROOT}")
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"DATA_DIR does not exist: {DATA_DIR}")
    if not SCRIPTS_DIR.exists():
        raise FileNotFoundError(f"SCRIPTS_DIR does not exist: {SCRIPTS_DIR}")

    print("\nCLEANING DATA DIRECTORIES")
    for folder in [TXT_DIR, CSV_DIR]:
        print(f"Clearing {folder}")
        delete_contents(folder)

    print(f"Deleting master file {MASTER_FILE}")
    delete_file(MASTER_FILE)

    print("\nSTARTING PIPELINE")
    for script in PIPELINE:
        run_script(script)

    print("\nPipeline finished successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        sys.exit(1)