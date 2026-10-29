"""Generate a realistic sample data file for demonstration.

Usage: python scripts/seed_data.py
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.storage import save_expenses

TEMPLATES = {
    "Food": (["Groceries", "Lunch at canteen", "Dinner with friends", "Tea and snacks", "Weekly vegetables"], 40, 900),
    "Travel": (["Metro card recharge", "Auto fare", "Bus pass", "Cab to station", "Train ticket"], 30, 1800),
    "Education": (["Reference book", "Online course", "Exam fee", "Printing notes", "Stationery"], 100, 4500),
    "Shopping": (["T-shirt", "Headphones", "Shoes", "Backpack", "Phone cover"], 250, 3500),
    "Entertainment": (["Movie ticket", "Streaming subscription", "Concert pass", "Gaming credit", "Weekend outing"], 120, 1500),
    "Other": (["Mobile recharge", "Medicine", "Haircut", "Gift", "Laundry"], 50, 1000),
}
WEIGHTS = {"Food": 38, "Travel": 22, "Education": 8, "Shopping": 12, "Entertainment": 12, "Other": 8}


def build(days: int = 180, seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    categories = list(WEIGHTS)
    weights = list(WEIGHTS.values())
    rows, today = [], date.today()
    for offset in range(days, -1, -1):
        for _ in range(rng.choice([0, 1, 1, 1, 2])):
            category = rng.choices(categories, weights)[0]
            names, low, high = TEMPLATES[category]
            amount = round(rng.triangular(low, high, low + (high - low) * 0.25), 2)
            rows.append(
                {
                    "id": len(rows) + 1,
                    "date": pd.Timestamp(today - timedelta(days=offset)),
                    "category": category,
                    "amount": amount,
                    "description": rng.choice(names),
                }
            )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    frame = build()
    save_expenses(frame)
    print(f"Wrote {len(frame)} sample records.")
