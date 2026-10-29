"""Input parsing and validation. Every parser raises ValueError with a readable message."""

from datetime import date, datetime

from .config import CATEGORIES, DATE_FORMAT, MAX_AMOUNT, MAX_DESCRIPTION


def parse_date(text: str) -> date:
    text = text.strip()
    try:
        parsed = datetime.strptime(text, DATE_FORMAT).date()
    except ValueError:
        raise ValueError("Date must be a real calendar date in YYYY-MM-DD format.")
    if parsed > date.today():
        raise ValueError("Date cannot be in the future.")
    return parsed


def parse_amount(text: str) -> float:
    cleaned = text.strip().replace(",", "")
    try:
        value = float(cleaned)
    except ValueError:
        raise ValueError("Amount must be a number, for example 249.50.")
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError("Amount must be a finite number.")
    if value <= 0:
        raise ValueError("Amount must be greater than zero.")
    if value > MAX_AMOUNT:
        raise ValueError(f"Amount cannot exceed {MAX_AMOUNT:,}.")
    return round(value, 2)


def parse_category(text: str) -> str:
    text = text.strip()
    if text.isdigit():
        index = int(text) - 1
        if 0 <= index < len(CATEGORIES):
            return CATEGORIES[index]
        raise ValueError(f"Choose a number between 1 and {len(CATEGORIES)}.")
    for name in CATEGORIES:
        if name.lower() == text.lower():
            return name
    raise ValueError("Unknown category. Pick a number or type a name from the list.")


def parse_description(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        raise ValueError("Description cannot be empty.")
    if len(text) > MAX_DESCRIPTION:
        raise ValueError(f"Description is limited to {MAX_DESCRIPTION} characters.")
    return text.replace(",", ";")


def parse_month(text: str) -> tuple[int, int]:
    try:
        parsed = datetime.strptime(text.strip(), "%Y-%m")
    except ValueError:
        raise ValueError("Month must be in YYYY-MM format, for example 2026-03.")
    return parsed.year, parsed.month


def parse_choice(text: str, valid: list[str]) -> str:
    text = text.strip().lower()
    if text not in valid:
        raise ValueError("Please choose one of: " + ", ".join(valid) + ".")
    return text
