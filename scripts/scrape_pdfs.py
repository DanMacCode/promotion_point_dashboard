import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define constants
BASE_URL = "https://www.ncoonfire.com/enlisted-cutoff-scores"
PDF_DIR = "../data/pdfs/"
os.makedirs(PDF_DIR, exist_ok=True)

# Function to extract the year and month from filenames
def extract_year_month(filename):
    match = re.search(r"(\bJAN|\bFEB|\bMAR|\bAPR|\bMAY|\bJUN|\bJUL|\bAUG|\bSEP|\bOCT|\bNOV|\bDEC)[-_]?(\d{2,4})", filename, re.IGNORECASE)
    if match:
        month, year = match.groups()
        month = month.upper()  # Normalize month format
        year = int(year[-4:] if len(year) == 4 else "20" + year)  # Normalize year
        return month, year
    return None, None

# Function to scrape all PDF links
def get_promotion_pdfs():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("❌ Failed to fetch webpage.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []

    # Extract all PDF links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)

    return pdf_links

# Function to download PDFs (Skipping pre-August 2023)
def download_pdfs():
    pdf_links = get_promotion_pdfs()
    if not pdf_links:
        print("❌ No PDFs found.")
        return

    for pdf_url in pdf_links:
        filename = pdf_url.split("/")[-1]  # Keep original filename
        month, year = extract_year_month(filename)

        # ✅ Skip PDFs before August 2023
        if year and month:
            if year < 2023 or (year == 2023 and month not in ["AUG", "SEP", "OCT", "NOV", "DEC"]):
                print(f"⏩ Skipping (Before Aug 2023): {filename}")
                continue  # Skip download

        file_path = os.path.join(PDF_DIR, filename)

        # Download and save PDF
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Failed to download: {pdf_url}")

# Run the scraper
if __name__ == "__main__":
    download_pdfs()
