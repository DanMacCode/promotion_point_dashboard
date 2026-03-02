import os
import re
from pathlib import Path

# Anchor to project root instead of using chdir + ../
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TXT_DIR = PROJECT_ROOT / "data" / "txt"

MONTH_MAP = {
    "JANUARY": "JAN",
    "FEBRUARY": "FEB",
    "MARCH": "MAR",
    "APRIL": "APR",
    "MAY": "MAY",
    "JUNE": "JUN",
    "JULY": "JUL",
    "AUGUST": "AUG",
    "SEPTEMBER": "SEP",
    "OCTOBER": "OCT",
    "NOVEMBER": "NOV",
    "DECEMBER": "DEC",
}

# Accept normalized files, including collision suffixes like _2, _3, etc.
ALREADY_RENAMED_RE = re.compile(
    r"^(ACTIVE|RESERVE)_[A-Z]{3}_[0-9]{2}(_\d+)?\.txt$",
    re.IGNORECASE,
)

# --- Everything below this line is unchanged ---


def generate_unique_filename(directory: Path, base_name: str) -> str:
    candidate = f"{base_name}.txt"
    if not (directory / candidate).exists():
        return candidate

    n = 2
    while True:
        candidate = f"{base_name}_{n}.txt"
        if not (directory / candidate).exists():
            return candidate
        n += 1


def normalize_month_to_abbrev(month_token: str) -> str | None:
    if not month_token:
        return None

    m = month_token.strip().upper()
    m = re.sub(r"[^A-Z]", "", m)

    if len(m) == 3 and m.isalpha():
        return m

    if m in MONTH_MAP:
        return MONTH_MAP[m]

    return None


def find_subject_line(lines: list[str]) -> str | None:
    """
    Returns the SUBJECT line, including wrapped continuation lines immediately following it.
    Stops when it reaches a blank line or a numbered paragraph (e.g., "1.").
    """
    for i, line in enumerate(lines):
        if "SUBJECT:" in line.upper():
            subject = line.strip()

            # Append up to a few continuation lines if the SUBJECT wraps
            for j in range(i + 1, min(i + 5, len(lines))):
                nxt = lines[j].strip()
                if not nxt:
                    break
                if re.match(r"^\d+\.", nxt):
                    break
                subject += " " + nxt

            return subject
    return None


def should_skip_file(subject_line: str | None, content_upper: str, filename_upper: str) -> bool:
    if "PROMOTION TREND REPORT" in content_upper:
        return True

    if "TREND_REPORT" in filename_upper:
        return True

    subject_upper = subject_line.upper() if subject_line else ""
    if "PROMOTION_POINT_CHANGES" in filename_upper:
        return True
    if "PROMOTION POINT CHANGES" in subject_upper:
        return True

    return False


def determine_component(subject_line: str | None, content_upper: str, filename_upper: str) -> str | None:
    subject_upper = subject_line.upper() if subject_line else ""

    reserve_subject_indicators = [
        "UNITED STATES ARMY RESERVE",
        "U.S. ARMY RESERVE",
        "US ARMY RESERVE",
        "ARMY RESERVE",
        "USAR",
        "ACTIVE GUARD RESERVE",
        "AGR",
    ]
    active_subject_indicators = [
        "ACTIVE ARMY",
        "REGULAR ARMY",
        "ACTIVE COMPONENT",
    ]

    if subject_upper:
        if any(ind in subject_upper for ind in reserve_subject_indicators):
            return "RESERVE"
        if any(ind in subject_upper for ind in active_subject_indicators):
            return "ACTIVE"

    if "AGR" in filename_upper or "-AGR-" in filename_upper or "_AGR_" in filename_upper:
        return "RESERVE"
    if "-AC-" in filename_upper or "_AC_" in filename_upper or "AC-CUTOFF-SCORES" in filename_upper:
        return "ACTIVE"

    if "AGR PROMOTION QUALIFICATION SCORES" in content_upper:
        return "RESERVE"
    if "AA PROMOTION QUALIFICATION SCORES" in content_upper:
        return "ACTIVE"

    reserve_content_indicators = [
        "ACTIVE GUARD RESERVE",
        "UNITED STATES ARMY RESERVE",
        "U.S. ARMY RESERVE",
        "US ARMY RESERVE",
        "ARMY RESERVE",
        "USAR",
        "AGR",
    ]
    active_content_indicators = [
        "ACTIVE ARMY",
        "REGULAR ARMY",
        "ACTIVE COMPONENT",
    ]

    reserve_hit = any(ind in content_upper for ind in reserve_content_indicators)
    active_hit = any(ind in content_upper for ind in active_content_indicators)

    if reserve_hit and not active_hit:
        return "RESERVE"
    if active_hit and not reserve_hit:
        return "ACTIVE"

    return None


def extract_month_year_from_subject(subject_line: str) -> tuple[str | None, str | None]:
    s = subject_line.strip()

    patterns = [
        r"\bfor\s+\d{1,2}\s+([A-Za-z]+)\s+(\d{4})\b",
        r"\bfor\s+([A-Za-z]+)\s+(\d{4})\b",
        r"\bmonth\s+of\s+([A-Za-z]+)\s+(\d{4})\b",
    ]

    for pat in patterns:
        m = re.search(pat, s, re.IGNORECASE)
        if m:
            mon = normalize_month_to_abbrev(m.group(1))
            yr = m.group(2)
            if mon and yr:
                return mon, yr

    return None, None


def extract_month_year_from_filename(filename: str) -> tuple[str | None, str | None]:
    base = Path(filename).stem.upper()

    m = re.search(r"(?<!\d)(\d{4})[\-_ ](\d{2})(?!\d)", base)
    if m:
        year = m.group(1)
        month_num = int(m.group(2))
        if 1 <= month_num <= 12:
            month_abbrev = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][
                month_num - 1
            ]
            return month_abbrev, year

    m = re.search(r"(?<![A-Z])([A-Z]{3,9})[\-_ ]+(\d{4})(?!\d)", base)
    if m:
        mon = normalize_month_to_abbrev(m.group(1))
        yr = m.group(2)
        if mon and yr:
            return mon, yr

    return None, None


def rename_txt_file(txt_path: Path) -> Path:
    if ALREADY_RENAMED_RE.match(txt_path.name):
        print(f"[SKIP] Already normalized: {txt_path.name}")
        return txt_path

    try:
        raw = txt_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[SKIP] Cannot read {txt_path.name}: {e}")
        return txt_path

    content_upper = raw.upper()
    filename_upper = txt_path.name.upper()

    lines = [ln.rstrip("\n") for ln in raw.splitlines()]
    subject_line = find_subject_line(lines)

    if should_skip_file(subject_line, content_upper, filename_upper):
        print(f"[SKIP] Non-series document: {txt_path.name}")
        return txt_path

    component = determine_component(subject_line, content_upper, filename_upper)
    if not component:
        print(f"[SKIP] Could not determine component (ACTIVE/RESERVE) for {txt_path.name}")
        return txt_path

    mon_abbrev = None
    year_4 = None
    if subject_line:
        mon_abbrev, year_4 = extract_month_year_from_subject(subject_line)

    if not mon_abbrev or not year_4:
        mon_abbrev, year_4 = extract_month_year_from_filename(txt_path.name)

    if not mon_abbrev or not year_4:
        print(f"[SKIP] Could not determine month/year for {txt_path.name}")
        return txt_path

    short_year = year_4[-2:]
    base_name = f"{component}_{mon_abbrev}_{short_year}"

    new_filename = generate_unique_filename(txt_path.parent, base_name)
    new_path = txt_path.parent / new_filename

    try:
        txt_path.rename(new_path)
        print(f"[RENAMED] {txt_path.name} -> {new_filename}")
        return new_path
    except Exception as e:
        print(f"[SKIP] Rename failed for {txt_path.name}: {e}")
        return txt_path


def rename_txts() -> None:
    if not TXT_DIR.exists():
        print(f"[ERROR] TXT_DIR not found: {TXT_DIR}")
        return

    for txt_path in sorted(TXT_DIR.glob("*.txt")):
        rename_txt_file(txt_path)


if __name__ == "__main__":
    rename_txts()