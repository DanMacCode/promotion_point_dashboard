import os
import re

# Set working directory to current file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))
TXT_DIR = "../data/txt"

def generate_unique_filename(directory, base_name):
    name = base_name
    count = 1
    while os.path.exists(os.path.join(directory, name + ".txt")):
        count += 1
        name = f"{base_name}_{count}"
    return name + ".txt"

def determine_component_from_subject(content):
    match = re.search(
        r"SUBJECT:\s*HQDA Promotion Point Cutoff Scores for \d+ (\w+) (\d{4}).*?for the (United States Army Reserve.*?|Active Army)",
        content,
        re.IGNORECASE
    )
    if not match:
        return None, None, None
    month, year, component_text = match.groups()
    component = "RESERVE" if "Reserve" in component_text else "ACTIVE"
    return month, year, component

def determine_component_from_cutoff(content):
    if "AGR PROMOTION QUALIFICATION SCORES" in content:
        return "RESERVE"
    elif "AA PROMOTION QUALIFICATION SCORES" in content:
        return "ACTIVE"
    else:
        return None

def rename_txt_file(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\n", " ")

    month, year, subject_component = determine_component_from_subject(content)
    if not month or not year or not subject_component:
        print(f"[SKIP] No SUBJECT line found in {txt_path}")
        return txt_path

    cutoff_component = determine_component_from_cutoff(content)
    component = cutoff_component if cutoff_component else subject_component

    short_month = month[:3].upper()
    short_year = year[-2:]
    base_name = f"{component}_{short_month}_{short_year}"

    new_filename = generate_unique_filename(os.path.dirname(txt_path), base_name)
    new_path = os.path.join(os.path.dirname(txt_path), new_filename)
    os.rename(txt_path, new_path)
    print(f"[RENAMED] {os.path.basename(txt_path)} → {new_filename}")
    return new_path

def rename_txts():
    for txt_filename in os.listdir(TXT_DIR):
        if txt_filename.endswith(".txt"):
            txt_path = os.path.join(TXT_DIR, txt_filename)
            if os.path.exists(txt_path):
                rename_txt_file(txt_path)
            else:
                print(f"[SKIP] File not found: {txt_path}")

if __name__ == "__main__":
    rename_txts()
