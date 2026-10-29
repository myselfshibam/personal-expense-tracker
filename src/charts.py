"""Matplotlib charts. Each builder returns a Figure; output() saves and optionally shows it."""

import io

import matplotlib.pyplot as plt
import pandas as pd

from . import analysis
from .config import CURRENCY, REPORT_DIR

THEMES = {
    "dark": {
        "bg": "#111827",
        "text": "#f1f5f9",
        "title": "#ffffff",
        "slate": "#94a3b8",
        "label": "#cbd5e1",
        "border": "#334155",
        "grid": "#1e293b",
        "primary": "#6366f1",
        "primary_edge": "#818cf8",
        "accent": "#f59e0b",
        "cyan": "#38bdf8",
        "palette": ["#6366f1", "#38bdf8", "#f59e0b", "#ec4899", "#10b981", "#8b5cf6", "#14b8a6"],
        "wedge_edge": "#111827",
    },
    "light": {
        "bg": "#ffffff",
        "text": "#1e293b",
        "title": "#0f172a",
        "slate": "#64748b",
        "label": "#475569",
        "border": "#cbd5e1",
        "grid": "#f1f5f9",
        "primary": "#4f46e5",
        "primary_edge": "#4338ca",
        "accent": "#d97706",
        "cyan": "#0284c7",
        "palette": ["#4f46e5", "#0284c7", "#d97706", "#db2777", "#059669", "#7c3aed", "#0d9488"],
        "wedge_edge": "#ffffff",
    },
}

# Compatibility constants
NAVY = "#6366f1"
SLATE = "#94a3b8"
ACCENT = "#f59e0b"
CYAN = "#38bdf8"
DARK_BG = "#111827"
PALETTE = THEMES["dark"]["palette"]


def _style(theme: str = "dark") -> dict:
    t = theme.lower() if theme else "dark"
    c = THEMES.get(t, THEMES["dark"])
    plt.rcParams.update(
        {
            "figure.facecolor": c["bg"],
            "axes.facecolor": c["bg"],
            "savefig.facecolor": c["bg"],
            "text.color": c["text"],
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.edgecolor": c["border"],
            "axes.labelcolor": c["slate"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlecolor": c["title"],
            "xtick.color": c["slate"],
            "ytick.color": c["slate"],
            "axes.grid": True,
            "grid.color": c["grid"],
            "grid.linewidth": 0.8,
            "axes.axisbelow": True,
        }
    )
    return c


def _require_data(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("There is no data to chart.")


def category_bar(df: pd.DataFrame, theme: str = "dark"):
    _require_data(df)
    c = _style(theme)
    totals = analysis.category_totals(df)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(totals.index, totals.values, color=c["primary"], width=0.6, edgecolor=c["primary_edge"], linewidth=0.8)
    ax.bar_label(bars, labels=[f"{v:,.0f}" for v in totals.values], padding=4, color=c["label"], fontsize=9, fontweight="bold")
    ax.set_title("Expenditure by Category")
    ax.set_ylabel(f"Amount ({CURRENCY})")
    ax.grid(axis="x", visible=False)
    ax.margins(y=0.14)
    fig.tight_layout()
    return fig


def category_pie(df: pd.DataFrame, theme: str = "dark"):
    _require_data(df)
    c = _style(theme)
    totals = analysis.category_totals(df)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    wedges, _, autotexts = ax.pie(
        totals.values,
        labels=totals.index,
        colors=c["palette"][: len(totals)],
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
        pctdistance=0.78,
        wedgeprops={"width": 0.44, "edgecolor": c["wedge_edge"], "linewidth": 2.5},
        textprops={"color": c["label"], "fontsize": 10},
    )
    for text in autotexts:
        text.set_color("#ffffff")
        text.set_fontsize(9)
        text.set_fontweight("bold")
    ax.text(0, 0, f"Total\n{CURRENCY} {totals.sum():,.0f}", ha="center", va="center", color=c["title"], fontweight="bold", fontsize=11)
    ax.set_title("Share of Spending by Category")
    ax.grid(False)
    fig.tight_layout()
    return fig


def spending_trend(df: pd.DataFrame, theme: str = "dark"):
    """Monthly line plot; falls back to a daily line when only one month exists."""
    _require_data(df)
    c = _style(theme)
    monthly = analysis.monthly_totals(df)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    if len(monthly) >= 2:
        labels = [str(p) for p in monthly.index]
        ax.plot(labels, monthly.values, color=c["cyan"], linewidth=2.4, marker="o", markersize=6, markerfacecolor=c["cyan"], markeredgecolor=c["bg"])
        ax.fill_between(labels, monthly.values, color=c["cyan"], alpha=0.12)
        for x, y in zip(labels, monthly.values):
            ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=c["label"], fontweight="bold")
        ax.set_title("Monthly Spending Trend")
        ax.set_xlabel("Month")
    else:
        daily = analysis.daily_totals(df)
        ax.plot(daily.index, daily.values, color=c["cyan"], linewidth=2.2, marker="o", markersize=5, markerfacecolor=c["cyan"])
        ax.fill_between(daily.index, daily.values, color=c["cyan"], alpha=0.12)
        ax.set_title("Daily Spending")
        ax.set_xlabel("Date")
        fig.autofmt_xdate()
    ax.set_ylabel(f"Amount ({CURRENCY})")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.08)
    fig.tight_layout()
    return fig


def amount_histogram(df: pd.DataFrame, theme: str = "dark"):
    _require_data(df)
    c = _style(theme)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bins = min(15, max(5, len(df) // 5))
    ax.hist(df["amount"], bins=bins, color=c["primary"], edgecolor=c["bg"], linewidth=1.2)
    mean = df["amount"].mean()
    ax.axvline(mean, color=c["accent"], linewidth=2.2, linestyle="--", label=f"Mean: {CURRENCY} {mean:,.0f}")
    ax.set_title("Distribution of Expense Amounts")
    ax.set_xlabel(f"Amount ({CURRENCY})")
    ax.set_ylabel("Number of expenses")
    legend = ax.legend(frameon=False)
    if legend:
        for text in legend.get_texts():
            text.set_color(c["label"])
    fig.tight_layout()
    return fig


CHART_BUILDERS = {
    "category_bar": category_bar,
    "category_pie": category_pie,
    "spending_trend": spending_trend,
    "amount_histogram": amount_histogram,
}


def output(fig, name: str, show: bool = True, theme: str = "dark") -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{name}.png"
    c = THEMES.get(theme.lower() if theme else "dark", THEMES["dark"])
    fig.savefig(path, dpi=150, facecolor=c["bg"], edgecolor="none")
    if show:
        plt.show()
    plt.close(fig)
    return str(path)


def to_png_bytes(fig, theme: str = "dark") -> bytes:
    """Render a figure to PNG bytes for the web interface."""
    buffer = io.BytesIO()
    c = THEMES.get(theme.lower() if theme else "dark", THEMES["dark"])
    fig.savefig(buffer, format="png", dpi=130, facecolor=c["bg"], edgecolor="none")
    plt.close(fig)
    return buffer.getvalue()


def generate_all(df: pd.DataFrame, show: bool = False, theme: str = "dark") -> list[str]:
    return [output(builder(df, theme=theme), name, show, theme=theme) for name, builder in CHART_BUILDERS.items()]
