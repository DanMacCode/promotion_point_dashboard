import os
import re
import pandas as pd

# Define directories
TXT_DIR = "../data/txt/"
CSV_DIR = "../data/csv/"
os.makedirs(CSV_DIR, exist_ok=True)

# Function to extract promotion data from a TXT file
def extract_promotion_data(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text_content = f.readlines()

    # Extract metadata (Date and Component)
    match = re.search(r"(ACTIVE|RESERVE)_(\w{3})_(\d{2})\.txt", os.path.basename(txt_path))
    if match:
        component, month, year = match.groups()
        date_str = f"20{year}-{month}"  # Convert to YYYY-MMM format
    else:
        date_str, component = "UNKNOWN", "UNKNOWN"

    # Identify all table start points
    table_start_indices = [i for i, line in enumerate(text_content) if "MOS SGT SSG SGT SSG SGT SSG" in line]

    # Extract relevant lines containing all table sections
    table_lines = []
    for start_idx in table_start_indices:
        for line in text_content[start_idx+1:]:  # Start after the header
            # Stop at the next section break (indicated by Notes, SUBJECT, or TOTALS)
            if "Note 1:" in line or "SUBJECT:" in line or "TOTALS" in line:
                break
            if line.strip():  # Ignore empty lines
                table_lines.append(line.strip())

    # Clean and parse the table
    data = []
    for line in table_lines:
        if re.match(r"^\d{2}[A-Z]", line):  # Identifies MOS codes at the start of the line
            values = re.split(r"\s+", line)  # Split by whitespace
            if len(values) == 7:
                values = [date_str, component] + values
                values = [pd.NA if v == "N/A" else v for v in values]  # Convert "N/A" to NaN
                data.append(values)

    # Create DataFrame with additional columns
    columns = ["Date", "Component", "MOS", "Cutoff_SGT", "Cutoff_SSG", "Eligibles_SGT", "Eligibles_SSG", "Promotions_SGT", "Promotions_SSG"]
    df = pd.DataFrame(data, columns=columns)

    # Save CSV with proper naming convention
    csv_filename = os.path.basename(txt_path).replace(".txt", ".csv")
    csv_path = os.path.join(CSV_DIR, csv_filename)
    df.to_csv(csv_path, index=False)
    print(f"✅ Extracted and saved: {csv_filename}")

    return csv_path

# Function to process all TXT files
def process_all_txt_files():
    for txt_filename in os.listdir(TXT_DIR):
        if txt_filename.endswith(".txt"):
            extract_promotion_data(os.path.join(TXT_DIR, txt_filename))

if __name__ == "__main__":
    process_all_txt_files()
