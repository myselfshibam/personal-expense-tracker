"""Plain-text formatting for tables and reports."""

from datetime import datetime

import pandas as pd

from . import analysis
from .config import CURRENCY, REPORT_DIR

WIDTH = 72


def money(value: float) -> str:
    return f"{CURRENCY} {value:,.2f}"


def rule(char: str = "-") -> str:
    return char * WIDTH


def heading(title: str) -> str:
    return f"\n{title.upper()}\n{rule()}"


def format_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No expenses to display."
    lines = [f"{'ID':>4}  {'Date':<10}  {'Category':<13}  {'Amount':>15}  Description", rule()]
    for row in df.itertuples():
        desc = row.description if len(row.description) <= 26 else row.description[:23] + "..."
        lines.append(
            f"{row.id:>4}  {row.date:%Y-%m-%d}  {row.category:<13}  {money(row.amount):>15}  {desc}"
        )
    lines.append(rule())
    lines.append(f"{len(df)} record(s)")
    return "\n".join(lines)


def format_breakdown(series: pd.Series) -> str:
    total = series.sum()
    lines = []
    for name, value in series.items():
        share = value / total * 100 if total else 0
        bar = "#" * int(round(share / 4))
        lines.append(f"  {str(name):<14}{money(value):>16}  {share:5.1f}%  {bar}")
    return "\n".join(lines)


def summary_text(df: pd.DataFrame) -> str:
    if df.empty:
        return "No expenses recorded yet."
    stats = analysis.average_stats(df)
    high, low = analysis.extremes(df)
    change = analysis.month_over_month(df)

    parts = [
        heading("Overall summary"),
        f"  Period covered      {df['date'].min():%d %b %Y} to {df['date'].max():%d %b %Y}",
        f"  Records             {len(df)}",
        f"  Total expenditure   {money(analysis.total_spent(df))}",
        f"  Average per expense {money(stats['per_expense'])}",
        f"  Median expense      {money(stats['median'])}",
        f"  Average per day     {money(stats['per_day'])}",
        f"  Average per month   {money(stats['per_month'])}",
    ]
    if change is not None:
        direction = "up" if change >= 0 else "down"
        parts.append(f"  Latest month        {direction} {abs(change):.1f}% on the previous month")

    parts += [
        heading("Largest and smallest"),
        f"  Highest  {money(high.amount)}  {high.category}, {high.description} ({high.date:%Y-%m-%d})",
        f"  Lowest   {money(low.amount)}  {low.category}, {low.description} ({low.date:%Y-%m-%d})",
        heading("By category"),
        format_breakdown(analysis.category_totals(df)),
        heading("By month"),
    ]
    for period, value in analysis.monthly_totals(df).items():
        parts.append(f"  {period}   {money(value):>16}")
    return "\n".join(parts)


def month_text(df: pd.DataFrame, year: int, month: int) -> str:
    subset = analysis.filter_month(df, year, month)
    label = f"{year}-{month:02d}"
    if subset.empty:
        return f"No expenses recorded for {label}."
    stats = analysis.average_stats(subset)
    high, low = analysis.extremes(subset)
    parts = [
        heading(f"Monthly report: {label}"),
        f"  Records             {len(subset)}",
        f"  Total expenditure   {money(analysis.total_spent(subset))}",
        f"  Average per expense {money(stats['per_expense'])}",
        f"  Highest             {money(high.amount)}  {high.description}",
        f"  Lowest              {money(low.amount)}  {low.description}",
        heading("By category"),
        format_breakdown(analysis.category_totals(subset)),
    ]
    return "\n".join(parts)


def export_summary(df: pd.DataFrame) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
    header = f"Personal Expense Tracker System - report generated {datetime.now():%d %b %Y, %H:%M}"
    path.write_text(f"{header}\n{rule('=')}{summary_text(df)}\n", encoding="utf-8")
    return str(path)
