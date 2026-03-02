from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LOCAL_CSV_PATH = BASE_DIR / "data" / "master" / "master_promotion_data.csv"

def load_master_df():
    df = pd.read_csv(LOCAL_CSV_PATH)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%b", errors="coerce")
    return df

def get_sorted_dates(df):
    if df is None or df.empty or "Date" not in df.columns:
        return []
    return df["Date"].dropna().sort_values().dt.strftime("%b-%Y").unique().tolist()