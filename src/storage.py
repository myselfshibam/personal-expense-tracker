"""CSV persistence for expense records."""

import os
from datetime import date
from pathlib import Path

import pandas as pd

from .config import COLUMNS, DATA_FILE, DATE_FORMAT


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "date": pd.Series(dtype="datetime64[ns]"),
            "category": pd.Series(dtype="object"),
            "amount": pd.Series(dtype="float64"),
            "description": pd.Series(dtype="object"),
        }
    )


def load_expenses(path: Path = DATA_FILE) -> tuple[pd.DataFrame, int]:
    """Read the CSV file. Returns the cleaned frame and the number of rows skipped."""
    if not path.exists() or path.stat().st_size == 0:
        return empty_frame(), 0

    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [c for c in COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"Data file is missing columns: {', '.join(missing)}")

    df = raw[COLUMNS].copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    invalid = df[["id", "date", "amount"]].isna().any(axis=1) | (df["amount"] <= 0)
    skipped = int(invalid.sum())
    df = df[~invalid].copy()
    df["id"] = df["id"].astype("int64")
    return df.reset_index(drop=True), skipped


def save_expenses(df: pd.DataFrame, path: Path = DATA_FILE) -> None:
    """Write to a temporary file first so a crash cannot corrupt the existing data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df[COLUMNS].copy()
    out["date"] = out["date"].dt.strftime(DATE_FORMAT)
    out["amount"] = out["amount"].map(lambda v: f"{v:.2f}")
    temp = path.with_suffix(".tmp")
    out.to_csv(temp, index=False)
    os.replace(temp, path)


def add_expense(df: pd.DataFrame, when: date, category: str, amount: float, description: str) -> pd.DataFrame:
    next_id = int(df["id"].max()) + 1 if len(df) else 1
    row = pd.DataFrame(
        [
            {
                "id": next_id,
                "date": pd.Timestamp(when),
                "category": category,
                "amount": amount,
                "description": description,
            }
        ]
    )
    return pd.concat([df, row], ignore_index=True) if len(df) else row


def delete_expense(df: pd.DataFrame, expense_id: int) -> tuple[pd.DataFrame, bool]:
    mask = df["id"] == expense_id
    if not mask.any():
        return df, False
    return df[~mask].reset_index(drop=True), True
