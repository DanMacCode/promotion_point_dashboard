import os
import re
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TXT_DIR = Path("../data/txt").resolve()

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
    # Hard excludes for non monthly cutoff series material
    if "PROMOTION TREND REPORT" in content_upper:
        return True

    # Also skip things that look like special reports by filename
    if "TREND_REPORT" in filename_upper:
        return True

    # Skip standalone "Promotion Point Changes" docs, but NOT cutoff memos that merely mention it in reminders
    subject_upper = subject_line.upper() if subject_line else ""
    if "PROMOTION_POINT_CHANGES" in filename_upper:
        return True
    if "PROMOTION POINT CHANGES" in subject_upper:
        return True

    return False


def determine_component(subject_line: str | None, content_upper: str, filename_upper: str) -> str | None:
    """
    Robust rule set (ordered by reliability):
      1) SUBJECT line classification (highest trust)
      2) Filename hints (AC vs AGR)
      3) Content markers specific to the COS tables
      4) As a last resort, content indicators (lowest trust)

    Always treat AGR as RESERVE.
    """
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

    # 1) SUBJECT line first (most accurate)
    if subject_upper:
        # AGR is always Reserve
        if any(ind in subject_upper for ind in reserve_subject_indicators):
            return "RESERVE"
        if any(ind in subject_upper for ind in active_subject_indicators):
            return "ACTIVE"

    # 2) Filename hints (common in scraped names like "*-AC-Cutoff-Scores*" or "*-AGR-Cutoff-Scores*")
    # Treat AGR as Reserve
    if "AGR" in filename_upper or "-AGR-" in filename_upper or "_AGR_" in filename_upper:
        return "RESERVE"
    # AC commonly means Active Component
    if "-AC-" in filename_upper or "_AC_" in filename_upper or "AC-CUTOFF-SCORES" in filename_upper:
        return "ACTIVE"

    # 3) COS table section markers
    if "AGR PROMOTION QUALIFICATION SCORES" in content_upper:
        return "RESERVE"
    if "AA PROMOTION QUALIFICATION SCORES" in content_upper:
        return "ACTIVE"

    # 4) Last resort: scan content, but DO NOT let a stray Reserve mention override everything.
    # If both appear in content, refuse to guess.
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
    """
    Prefer the effective month and year.
    Handles:
      - for 01 December 2025
      - for 1 April 2025
      - for December 2025
      - for the month of December 2025
    """
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
    """
    Useful fallbacks:
      - HQDA_COS_as_of_20_NOV_2025 -> NOV 2025
      - HQDA_COS_-_2026-02_-_as_of_20_JAN_2026 -> 2026-02
      - August-2023-AC-Cutoff-Scores -> AUG 2023
    """
    base = Path(filename).stem.upper()

    # YYYY-MM pattern (avoid \b because "_" is a word character)
    m = re.search(r"(?<!\d)(\d{4})[\-_ ](\d{2})(?!\d)", base)
    if m:
        year = m.group(1)
        month_num = int(m.group(2))
        if 1 <= month_num <= 12:
            month_abbrev = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][
                month_num - 1
            ]
            return month_abbrev, year

    # Month-name + YYYY (e.g., AUGUST-2023 or Aug-2023)
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

    # Prefer effective month/year from SUBJECT
    mon_abbrev = None
    year_4 = None
    if subject_line:
        mon_abbrev, year_4 = extract_month_year_from_subject(subject_line)

    # Fallback to filename parsing
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