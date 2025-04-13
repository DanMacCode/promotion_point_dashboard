import os
import pdfplumber

# Define directories
PDF_DIR = "../data/pdfs/"
TXT_DIR = "../data/txt/"
os.makedirs(TXT_DIR, exist_ok=True)

# Function to convert PDFs to TXT
def convert_pdf_to_txt(pdf_filename):
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    txt_filename = pdf_filename.replace(".pdf", ".txt")
    txt_path = os.path.join(TXT_DIR, txt_filename)

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Converted {pdf_filename} → {txt_filename}")
    return txt_path

# Process all PDFs
if __name__ == "__main__":
    for pdf_file in os.listdir(PDF_DIR):
        if pdf_file.endswith(".pdf"):
            convert_pdf_to_txt(pdf_file)
