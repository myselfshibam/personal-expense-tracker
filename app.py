"""Web interface. Run with `python app.py`, then open in Safari or any browser."""

import os
import socket
import threading
import webbrowser
from datetime import date

import matplotlib

matplotlib.use("Agg")  # render charts to memory; no desktop window needed

from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for

from src import analysis, charts, storage, validators
from src.config import CATEGORIES, CURRENCY

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def is_port_in_use(port: int, host: str = HOST) -> bool:
    """Check if a network port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def get_available_port(preferred: int = 5000, fallbacks: tuple[int, ...] = (5050, 5003, 5004, 8080)) -> int:
    """Return preferred port or the first free fallback port (e.g. if macOS AirPlay holds 5000)."""
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass

    if not is_port_in_use(preferred):
        return preferred
    for p in fallbacks:
        if not is_port_in_use(p):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "personal-expense-tracker-system-local-session"


@app.template_filter("money")
def money_filter(value: float) -> str:
    return f"{CURRENCY} {value:,.2f}"


@app.route("/")
def dashboard():
    df, skipped = storage.load_expenses()
    if df.empty:
        return render_template("dashboard.html", empty=True)

    total = analysis.total_spent(df)
    high, low = analysis.extremes(df)
    context = {
        "empty": False,
        "count": len(df),
        "total": total,
        "stats": analysis.average_stats(df),
        "change": analysis.month_over_month(df),
        "high": high.to_dict(),
        "low": low.to_dict(),
        "categories": [(n, v, v / total * 100) for n, v in analysis.category_totals(df).items()],
        "months": [(str(p), v) for p, v in analysis.monthly_totals(df).items()],
        "recent": analysis.sort_expenses(df, "date", ascending=False).head(8).to_dict("records"),
        "period": (df["date"].min(), df["date"].max()),
        "skipped": skipped,
    }
    return render_template("dashboard.html", **context)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = {"date": date.today().isoformat(), "category": "", "amount": "", "description": ""}
    errors = {}
    if request.method == "POST":
        form = {key: request.form.get(key, "") for key in form}
        parsers = {
            "date": validators.parse_date,
            "category": validators.parse_category,
            "amount": validators.parse_amount,
            "description": validators.parse_description,
        }
        values = {}
        for field, parser in parsers.items():
            try:
                values[field] = parser(form[field])
            except ValueError as error:
                errors[field] = str(error)
        if not errors:
            df, _ = storage.load_expenses()
            df = storage.add_expense(df, values["date"], values["category"], values["amount"], values["description"])
            storage.save_expenses(df)
            flash("Expense saved.", "success")
            return redirect(url_for("add"))
    return render_template("add.html", form=form, errors=errors, categories=CATEGORIES)


@app.route("/expenses")
def expenses():
    df, _ = storage.load_expenses()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "")

    if category in CATEGORIES:
        df = df[df["category"] == category]
    if keyword:
        df = analysis.search_expenses(df, keyword)
    try:
        df = analysis.sort_expenses(df, sort_by, ascending=(order == "asc"))
    except ValueError:
        sort_by = "date"
        df = analysis.sort_expenses(df, "date", ascending=(order == "asc"))

    return render_template(
        "expenses.html",
        rows=df.to_dict("records"),
        total=analysis.total_spent(df),
        sort_by=sort_by,
        order=order,
        keyword=keyword,
        category=category,
        categories=CATEGORIES,
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id: int):
    df, _ = storage.load_expenses()
    df, removed = storage.delete_expense(df, expense_id)
    if removed:
        storage.save_expenses(df)
        flash("Expense deleted.", "success")
    else:
        flash("That expense no longer exists.", "error")
    return redirect(request.referrer or url_for("expenses"))


@app.route("/monthly")
def monthly():
    df, _ = storage.load_expenses()
    if df.empty:
        return render_template("monthly.html", empty=True)

    available = [str(p) for p in analysis.monthly_totals(df).index]
    chosen = request.args.get("month", available[-1])
    try:
        year, month = validators.parse_month(chosen)
    except ValueError:
        flash("Month must be in YYYY-MM format.", "error")
        chosen = available[-1]
        year, month = validators.parse_month(chosen)

    subset = analysis.filter_month(df, year, month)
    context = {"empty": False, "available": available, "chosen": chosen, "has_data": not subset.empty}
    if not subset.empty:
        total = analysis.total_spent(subset)
        high, low = analysis.extremes(subset)
        context.update(
            count=len(subset),
            total=total,
            stats=analysis.average_stats(subset),
            high=high.to_dict(),
            low=low.to_dict(),
            categories=[(n, v, v / total * 100) for n, v in analysis.category_totals(subset).items()],
            rows=analysis.sort_expenses(subset, "date", ascending=True).to_dict("records"),
        )
    return render_template("monthly.html", **context)


@app.route("/charts")
def chart_page():
    df, _ = storage.load_expenses()
    return render_template("charts.html", empty=df.empty)


@app.route("/chart/<name>.png")
def chart_image(name: str):
    builder = charts.CHART_BUILDERS.get(name)
    df, _ = storage.load_expenses()
    if builder is None or df.empty:
        abort(404)
    theme = request.args.get("theme", "dark").lower()
    if theme not in ("dark", "light"):
        theme = "dark"
    return Response(charts.to_png_bytes(builder(df, theme=theme), theme=theme), mimetype="image/png")


def open_browser(target_url: str = URL) -> None:
    try:
        webbrowser.get("safari").open(target_url)  # available on macOS
    except webbrowser.Error:
        webbrowser.open(target_url)


if __name__ == "__main__":
    active_port = get_available_port(PORT)
    active_url = f"http://{HOST}:{active_port}"

    if active_port != PORT:
        print(f"\n  [Notice] Port {PORT} is currently in use (commonly by macOS AirPlay Receiver).")
        print(f"  Automatically switching to free port: {active_port}")

    print(f"\n  Personal Expense Tracker System is running at {active_url}")
    print("  Press Ctrl+C in this window to stop.\n")
    threading.Timer(1.0, lambda: open_browser(active_url)).start()
    app.run(host=HOST, port=active_port, debug=False)
