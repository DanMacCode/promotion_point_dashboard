import os
import pandas as pd

# Define directories
CSV_DIR = "../data/csv/"
MASTER_DIR = "../data/master/"
os.makedirs(MASTER_DIR, exist_ok=True)

# Master dataset output path
MASTER_FILE = os.path.join(MASTER_DIR, "master_promotion_data.csv")

def compile_all_csvs():
    all_data = []

    for csv_filename in os.listdir(CSV_DIR):
        if csv_filename.endswith(".csv"):
            csv_path = os.path.join(CSV_DIR, csv_filename)
            df = pd.read_csv(csv_path)
            all_data.append(df)

    if all_data:
        # Combine all datasets into one
        master_df = pd.concat(all_data, ignore_index=True)

        # Save as master CSV
        master_df.to_csv(MASTER_FILE, index=False)
        print(f"✅ Compiled all CSVs into {MASTER_FILE}")

if __name__ == "__main__":
    compile_all_csvs()
