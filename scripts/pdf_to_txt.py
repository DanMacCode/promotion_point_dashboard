import os
from pathlib import Path
import pdfplumber

# Anchor paths to the repo root so this works locally and in Railway
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
TXT_DIR = PROJECT_ROOT / "data" / "txt"

PDF_DIR.mkdir(parents=True, exist_ok=True)
TXT_DIR.mkdir(parents=True, exist_ok=True)

def convert_pdf_to_txt(pdf_filename: str) -> Path:
    pdf_path = PDF_DIR / pdf_filename
    txt_filename = pdf_filename.replace(".pdf", ".txt")
    txt_path = TXT_DIR / txt_filename

    with pdfplumber.open(str(pdf_path)) as pdf:
        text = "\n".join(
            [page.extract_text() for page in pdf.pages if page.extract_text()]
        )

    txt_path.write_text(text, encoding="utf-8")

    return txt_path


if __name__ == "__main__":
    pdf_files = [f for f in PDF_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    total = len(pdf_files)

    for i, pdf_file in enumerate(pdf_files, start=1):
        convert_pdf_to_txt(pdf_file.name)
        percent = (i / total) * 100 if total else 100
        print(f"Converted {pdf_file.name} | {percent:.2f}% complete")