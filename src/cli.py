"""Menu-driven command line interface."""

from datetime import date

from . import analysis, charts, report, storage, validators
from .config import CATEGORIES, DATA_FILE
from .report import rule


class Cancelled(Exception):
    """Raised when the user abandons the current action."""


def ask(label: str, parser, default: str | None = None):
    """Prompt until the parser accepts the input. Typing 'cancel' aborts."""
    suffix = f" [{default}]" if default else ""
    while True:
        text = input(f"  {label}{suffix}: ").strip()
        if text.lower() == "cancel":
            raise Cancelled
        if not text and default is not None:
            text = default
        try:
            return parser(text)
        except ValueError as error:
            print(f"  Invalid input. {error}")


def pause() -> None:
    input("\n  Press Enter to continue...")


def banner() -> None:
    print("\n" + rule("="))
    print("  PERSONAL EXPENSE TRACKER SYSTEM")
    print(rule("="))


def menu() -> str:
    options = [
        ("1", "Add expense"),
        ("2", "View and sort expenses"),
        ("3", "Overall summary"),
        ("4", "Monthly report"),
        ("5", "Search or delete an expense"),
        ("6", "Charts"),
        ("7", "Export summary report"),
        ("0", "Exit"),
    ]
    print()
    for key, text in options:
        print(f"  {key}.  {text}")
    return input("\n  Select an option: ").strip()


def add_flow(df):
    print(report.heading("Add expense"))
    print("  Type 'cancel' at any prompt to return to the menu.\n")
    when = ask("Date (YYYY-MM-DD)", validators.parse_date, default=date.today().isoformat())
    print("\n  Categories")
    for number, name in enumerate(CATEGORIES, start=1):
        print(f"    {number}. {name}")
    print()
    category = ask("Category (number or name)", validators.parse_category)
    amount = ask("Amount", validators.parse_amount)
    description = ask("Description", validators.parse_description)

    df = storage.add_expense(df, when, category, amount, description)
    storage.save_expenses(df)
    print(f"\n  Saved: {when:%Y-%m-%d}  {category}  {report.money(amount)}  {description}")
    return df


def view_flow(df):
    print(report.heading("View and sort expenses"))
    if df.empty:
        print("  No expenses recorded yet.")
        return
    fields = ["date", "amount", "category", "description", "id"]
    by = ask(f"Sort by ({'/'.join(fields)})", lambda t: validators.parse_choice(t, fields), default="date")
    order = ask("Order (asc/desc)", lambda t: validators.parse_choice(t, ["asc", "desc"]), default="desc")
    ordered = analysis.sort_expenses(df, by, ascending=(order == "asc"))
    print()
    print(report.format_table(ordered))


def month_flow(df):
    print(report.heading("Monthly report"))
    if df.empty:
        print("  No expenses recorded yet.")
        return
    latest = df["date"].max()
    default = f"{latest.year}-{latest.month:02d}"
    year, month = ask("Month (YYYY-MM)", validators.parse_month, default=default)
    print(report.month_text(df, year, month))


def manage_flow(df):
    print(report.heading("Search or delete"))
    if df.empty:
        print("  No expenses recorded yet.")
        return df
    action = ask("Action (search/delete)", lambda t: validators.parse_choice(t, ["search", "delete"]), default="search")

    if action == "search":
        keyword = ask("Keyword in description", validators.parse_description)
        print()
        print(report.format_table(analysis.search_expenses(df, keyword)))
        return df

    def parse_id(text):
        if not text.isdigit():
            raise ValueError("ID must be a whole number.")
        return int(text)

    expense_id = ask("ID of the expense to delete", parse_id)
    match = df[df["id"] == expense_id]
    if match.empty:
        print(f"  No expense with ID {expense_id}.")
        return df
    print()
    print(report.format_table(match))
    confirm = ask("Delete this record? (yes/no)", lambda t: validators.parse_choice(t, ["yes", "no"]), default="no")
    if confirm == "no":
        print("  Nothing deleted.")
        return df
    df, _ = storage.delete_expense(df, expense_id)
    storage.save_expenses(df)
    print("  Record deleted.")
    return df


def chart_flow(df):
    print(report.heading("Charts"))
    if df.empty:
        print("  No expenses recorded yet.")
        return
    choices = {
        "1": ("Bar chart: spending by category", "category_bar"),
        "2": ("Pie chart: share by category", "category_pie"),
        "3": ("Line plot: spending trend", "spending_trend"),
        "4": ("Histogram: expense amounts", "amount_histogram"),
        "5": ("Generate all and save only", None),
    }
    for key, (label, _) in choices.items():
        print(f"  {key}. {label}")
    print()
    pick = ask("Choice", lambda t: validators.parse_choice(t, list(choices)))
    name = choices[pick][1]
    if name is None:
        for path in charts.generate_all(df, show=False):
            print(f"  Saved {path}")
        return
    path = charts.output(charts.CHART_BUILDERS[name](df), name, show=True)
    print(f"  Saved {path}")


def run() -> None:
    banner()
    try:
        df, skipped = storage.load_expenses()
    except (ValueError, OSError) as error:
        print(f"\n  Could not read {DATA_FILE.name}: {error}")
        return
    if skipped:
        print(f"\n  Note: {skipped} invalid row(s) in the data file were ignored.")
    print(f"  {len(df)} record(s) loaded.")

    while True:
        choice = menu()
        if choice == "0":
            print("\n  Goodbye.\n")
            return
        try:
            if choice == "1":
                df = add_flow(df)
            elif choice == "2":
                view_flow(df)
            elif choice == "3":
                print(report.summary_text(df))
            elif choice == "4":
                month_flow(df)
            elif choice == "5":
                df = manage_flow(df)
            elif choice == "6":
                chart_flow(df)
            elif choice == "7":
                if df.empty:
                    print("\n  No expenses recorded yet.")
                else:
                    print(f"\n  Report written to {report.export_summary(df)}")
            else:
                print("\n  Please enter a number from the menu.")
                continue
        except Cancelled:
            print("\n  Cancelled.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye.\n")
            return
        except OSError as error:
            print(f"\n  File error: {error}")
        pause()
