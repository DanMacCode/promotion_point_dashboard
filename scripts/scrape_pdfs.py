import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

print("[INFO] Waiting 2 seconds to avoid request spike...")
time.sleep(2)

# Define constants
BASE_URL = "https://www.ncoonfire.com/enlisted-cutoff-scores"
PDF_DIR = "../data/pdfs/"
os.makedirs(PDF_DIR, exist_ok=True)

# Function to extract the year and month from filenames
def extract_year_month(filename):
    match = re.search(r"(\bJAN|\bFEB|\bMAR|\bAPR|\bMAY|\bJUN|\bJUL|\bAUG|\bSEP|\bOCT|\bNOV|\bDEC)[-_]?(\d{2,4})", filename, re.IGNORECASE)
    if match:
        month, year = match.groups()
        month = month.upper()
        year = int(year[-4:] if len(year) == 4 else "20" + year)  # Normalize year
        return month, year
    return None, None

# Function to scrape all PDF links
def get_promotion_pdfs():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Failed to fetch webpage.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)

    return pdf_links

# Function to download PDFs
def download_pdfs():
    pdf_links = get_promotion_pdfs()
    if not pdf_links:
        print("No PDFs found.")
        return

    for pdf_url in pdf_links:
        print(f"[INFO] Fetching URL: {pdf_url}")
        filename = pdf_url.split("/")[-1]
        month, year = extract_year_month(filename)

        if year and month:
            if year < 2023 or (year == 2023 and month not in ["AUG", "SEP", "OCT", "NOV", "DEC"]):
                print(f"[INFO] Skipping (Before Aug 2023): {filename}")
                continue

        file_path = os.path.join(PDF_DIR, filename)

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(pdf_url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"[SUCCESS] Downloaded: {filename}")
            else:
                print(f"[WARN] Failed to download {pdf_url} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Exception downloading {pdf_url}: {e}")

# Entry point
if __name__ == "__main__":
    download_pdfs()
