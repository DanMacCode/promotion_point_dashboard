import os
import re

# Define directories
TXT_DIR = "../data/txt/"

# Function to extract metadata from SUBJECT line
def extract_metadata_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read().replace("\n", " ")  # Join all lines into one to handle multi-line subject lines

    # Updated regex to capture dates and component type across multiple lines
    match = re.search(
        r"SUBJECT:\s*HQDA Promotion Point Cutoff Scores for \d+ (\w+) (\d{4}).*for the (Active Army|United States Army Reserve, Active Guard Reserve)",
        text,
        re.IGNORECASE
    )

    if match:
        month, year, component = match.groups()
        short_month = month[:3].upper()  # Convert to three-letter format (e.g., FEB)
        year = year[-2:]  # Use last two digits (e.g., 25 for 2025)
        component = "RESERVE" if "Reserve" in component else "ACTIVE"
        return f"{component}_{short_month}_{year}"
    return None

# Function to rename TXT files safely
def rename_txts():
    rename_map = {}

    for txt_filename in os.listdir(TXT_DIR):
        if txt_filename.endswith(".txt"):
            txt_path = os.path.join(TXT_DIR, txt_filename)

            # Extract metadata from SUBJECT line
            new_filename = extract_metadata_from_txt(txt_path)
            if new_filename:
                new_txt_path = os.path.join(TXT_DIR, f"{new_filename}.txt")

                # Ensure original file exists before renaming
                if os.path.exists(txt_path):
                    rename_map[txt_path] = new_txt_path
                else:
                    print(f"⚠️ Skipping (File Not Found): {txt_path}")

    # Perform renaming
    for old_path, new_path in rename_map.items():
        os.rename(old_path, new_path)
        print(f"✅ Renamed TXT: {os.path.basename(old_path)} → {os.path.basename(new_path)}")

if __name__ == "__main__":
    rename_txts()
