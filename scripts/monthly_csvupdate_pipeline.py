import os
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import subprocess
import time
from dotenv import load_dotenv
import pdfplumber
import re
import urllib.parse


# === Initial Setup ===
load_dotenv()
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://www.ncoonfire.com/enlisted-cutoff-scores"
PDF_DIR = os.path.join(ROOT_DIR, "data", "pdfs")
TXT_DIR = os.path.join(ROOT_DIR, "data", "txt")
CSV_DIR = os.path.join(ROOT_DIR, "data", "csv")
MASTER_CSV = os.path.join(ROOT_DIR, "data", "master", "master_promotion_data.csv")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MASTER_CSV), exist_ok=True)

# === Get Latest Date from Master CSV ===
def get_latest_date():
    if not os.path.exists(MASTER_CSV):
        return None
    df = pd.read_csv(MASTER_CSV)
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    return df["Date"].max()

# === Scrape Page for Available PDFs ===
def get_available_pdfs():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)
    return pdf_links

# === Download PDF ===
def download_pdf(url):
    filename = url.split("/")[-1]
    local_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(local_path):
        return local_path
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200 and b"%PDF" in r.content[:1024]:
        with open(local_path, "wb") as f:
            f.write(r.content)
        print(f"[DOWNLOADED] {filename}")
        return local_path
    else:
        print(f"[SKIPPED] No valid PDF at: {url}")
        return None

# === Convert PDF to TXT ===
def convert_pdf_to_txt(pdf_path):
    filename = os.path.basename(pdf_path).replace(".pdf", ".txt")
    txt_path = os.path.join(TXT_DIR, filename)
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[CONVERTED] {filename}")
    return txt_path

# === Rename TXT File ===
def rename_txt_file(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read().replace("\n", " ")
    match = re.search(
        r"SUBJECT:\s*HQDA Promotion Point Cutoff Scores for \d+ (\w+) (\d{4}).*for the (Active Army|United States Army Reserve, Active Guard Reserve)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return txt_path
    month, year, component = match.groups()
    short_month = month[:3].upper()
    short_year = year[-2:]
    component = "RESERVE" if "Reserve" in component else "ACTIVE"
    new_filename = f"{component}_{short_month}_{short_year}.txt"
    new_path = os.path.join(TXT_DIR, new_filename)

    if os.path.exists(new_path):
        print(f"[SKIP RENAME] File already exists: {new_filename}")
        os.remove(txt_path)
        return new_path

    os.rename(txt_path, new_path)
    print(f"[RENAMED] {os.path.basename(txt_path)} → {new_filename}")
    return new_path

# === Convert TXT to CSV ===
def txt_to_csv(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    match = re.search(r"(ACTIVE|RESERVE)_(\w{3})_(\d{2})\\.txt", os.path.basename(txt_path))
    if match:
        component, month, year = match.groups()
        date_str = f"20{year}-{month}"
    else:
        date_str, component = "UNKNOWN", "UNKNOWN"

    table_start = [i for i, line in enumerate(lines) if "MOS SGT SSG SGT SSG SGT SSG" in line]
    table_lines = []
    for start_idx in table_start:
        for line in lines[start_idx+1:]:
            if any(x in line for x in ["Note 1:", "SUBJECT:", "TOTALS"]):
                break
            if line.strip():
                table_lines.append(line.strip())

    data = []
    for line in table_lines:
        if re.match(r"^\d{2}[A-Z]", line):
            values = re.split(r"\\s+", line)
            if len(values) == 7:
                values = [date_str, component] + [pd.NA if v == "N/A" else v for v in values]
                data.append(values)

    columns = ["Date", "Component", "MOS", "Cutoff_SGT", "Cutoff_SSG", "Eligibles_SGT",
               "Eligibles_SSG", "Promotions_SGT", "Promotions_SSG"]
    df = pd.DataFrame(data, columns=columns)
    csv_filename = os.path.basename(txt_path).replace(".txt", ".csv")
    csv_path = os.path.join(CSV_DIR, csv_filename)
    df.to_csv(csv_path, index=False)
    print(f"[CSV SAVED] {csv_filename}")
    return csv_path, df

# === Append to Master CSV ===
def append_to_master(df):
    if os.path.exists(MASTER_CSV):
        master_df = pd.read_csv(MASTER_CSV)
        final_df = pd.concat([master_df, df], ignore_index=True).drop_duplicates()
    else:
        final_df = df
    final_df.to_csv(MASTER_CSV, index=False)
    print("[MASTER UPDATED]")

# === Git Push Function ===
def git_push():
    try:
        subprocess.run(["git", "add", MASTER_CSV], check=True)
        subprocess.run(["git", "commit", "-m", "Monthly update to master CSV"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[GIT PUSHED]")
    except subprocess.CalledProcessError as e:
        print(f"[GIT ERROR] {e}")

# === SimplePush Notification ===
def send_push_notification(update_available=True):
    channel_key = os.getenv("SIMPLEPUSH_KEY")
    if not channel_key:
        print("[ERROR] SIMPLEPUSH_KEY not found.")
        return

    title = "Promotion Update Complete" if update_available else "No New Promotion Update"
    message = "Promotion Point Dashboard updated and pushed to GitHub." if update_available else "Checked for updates: no new data was added to the dashboard."

    # Encode title and message for URL
    encoded_title = urllib.parse.quote(title)
    encoded_message = urllib.parse.quote(message)

    url = f"https://simplepu.sh/{channel_key}/{encoded_title}/{encoded_message}"

    try:
        r = requests.get(url)
        if r.status_code == 200:
            print("[NOTIFICATION SENT]")
        else:
            print(f"[NOTIFICATION FAILED] {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[NOTIFICATION FAILED] Exception - {e}")

# === Main Execution ===
def main():
    print("[START] Monthly Update Check")
    latest_date = get_latest_date()
    pdf_urls = get_available_pdfs()
    new_update_found = False  # <== FLAG

    for url in sorted(pdf_urls, reverse=True):
        local_pdf = download_pdf(url)
        if not local_pdf:
            continue

        filename = os.path.basename(local_pdf).replace(".pdf", "")
        match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-_ ]?(\d{2,4})", filename, re.IGNORECASE)
        if match:
            month_str, year_str = match.groups()
            try:
                year_str = year_str if len(year_str) == 4 else f"20{year_str}"
                file_date = datetime.strptime(f"{month_str} {year_str}", "%b %Y")
                if file_date < datetime(2023, 8, 1):
                    print(f"[SKIP] {filename} is before August 2023.")
                    continue
            except ValueError:
                print(f"[SKIP] Could not parse date from: {filename}")
                continue
        else:
            print(f"[SKIP] No recognizable date in filename: {filename}")
            continue

        txt_path = convert_pdf_to_txt(local_pdf)
        renamed_txt = rename_txt_file(txt_path)

        match = re.search(r"(ACTIVE|RESERVE)_(\w{3})_(\d{2})\.txt", os.path.basename(renamed_txt))
        if not match:
            print(f"[SKIP] Filename does not match expected format: {renamed_txt}")
            continue

        csv_path, df = txt_to_csv(renamed_txt)
        if df.empty:
            print(f"[SKIP] No usable data extracted from {renamed_txt}")
            continue

        update_date = pd.to_datetime(df["Date"].iloc[0], errors="coerce")
        if latest_date and update_date <= latest_date:
            print("[SKIP] Already up to date.")
            break

        append_to_master(df)
        git_push()
        send_push_notification(update_available=True)
        new_update_found = True
        break  # Stop after first successful update

    if not new_update_found:
        send_push_notification(update_available=False)

    print("[DONE] Pipeline Complete")


if __name__ == "__main__":
    main()