"""Spending calculations built on pandas. All functions are pure and return new objects."""

import pandas as pd


def total_spent(df: pd.DataFrame) -> float:
    return float(df["amount"].sum())


def monthly_totals(df: pd.DataFrame) -> pd.Series:
    return df.groupby(df["date"].dt.to_period("M"))["amount"].sum().sort_index()


def category_totals(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)


def daily_totals(df: pd.DataFrame) -> pd.Series:
    return df.groupby(df["date"].dt.normalize())["amount"].sum().sort_index()


def filter_month(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    mask = (df["date"].dt.year == year) & (df["date"].dt.month == month)
    return df[mask].reset_index(drop=True)


def average_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"per_expense": 0.0, "median": 0.0, "per_day": 0.0, "per_month": 0.0}
    span_days = (df["date"].max() - df["date"].min()).days + 1
    months = df["date"].dt.to_period("M").nunique()
    total = total_spent(df)
    return {
        "per_expense": float(df["amount"].mean()),
        "median": float(df["amount"].median()),
        "per_day": total / span_days,
        "per_month": total / months,
    }


def extremes(df: pd.DataFrame):
    """Return (highest, lowest) expense rows, or (None, None) for empty data."""
    if df.empty:
        return None, None
    return df.loc[df["amount"].idxmax()], df.loc[df["amount"].idxmin()]


def sort_expenses(df: pd.DataFrame, by: str, ascending: bool = True) -> pd.DataFrame:
    allowed = {"date", "amount", "category", "description", "id"}
    if by not in allowed:
        raise ValueError(f"Cannot sort by '{by}'.")
    return df.sort_values(by, ascending=ascending, kind="stable").reset_index(drop=True)


def search_expenses(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    mask = df["description"].str.contains(keyword, case=False, regex=False)
    return df[mask].reset_index(drop=True)


def month_over_month(df: pd.DataFrame):
    """Percentage change between the two most recent months, or None if unavailable."""
    totals = monthly_totals(df)
    if len(totals) < 2 or totals.iloc[-2] == 0:
        return None
    return float((totals.iloc[-1] - totals.iloc[-2]) / totals.iloc[-2] * 100)
