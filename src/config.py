"""Application-wide settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
DATA_FILE = DATA_DIR / "expenses.csv"

COLUMNS = ["id", "date", "category", "amount", "description"]
CATEGORIES = ["Food", "Travel", "Education", "Shopping", "Entertainment", "Other"]

DATE_FORMAT = "%Y-%m-%d"
CURRENCY = "Rs."
MAX_AMOUNT = 10_000_000
MAX_DESCRIPTION = 60
