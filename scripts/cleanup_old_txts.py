import os

TXT_DIR = "../data/txt/"
CUTOFF_YEAR = 2023

def should_delete(filename):
    match = re.search(r"_(\w+)_(\w+)_(\d{4})", filename)
    if match:
        _, month, year = match.groups()
        year = int(year)
        allowed_months = ["AUG", "SEP", "OCT", "NOV", "DEC"]

        # If year is before 2023 or before August in 2023, mark for deletion
        if year < CUTOFF_YEAR or (year == CUTOFF_YEAR and month not in allowed_months):
            return True
    return False

def cleanup_old_txts():
    deleted_files = []
    for filename in os.listdir(TXT_DIR):
        if filename.endswith('.txt') and should_delete(filename):
            file_path = os.path.join(TXT_DIR, filename)
            os.remove(file_path)
            deleted_files.append(filename)
            print(f"🗑 Deleted: {filename}")

    # Log deleted files
    with open("deleted_files.log", "w") as log:
        log.write("\n".join(deleted_files))

if __name__ == "__main__":
    cleanup_old_txts()
