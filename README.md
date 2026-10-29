# Personal Expense Tracker System

A menu-driven Python application for recording daily expenses, analysing spending
patterns and producing graphical reports. Built with Python, Pandas and Matplotlib.

## Features

| Area | Capability |
|------|------------|
| Recording | Add expenses with date, category, amount and description |
| Categories | Food, Travel, Education, Shopping, Entertainment, Other |
| Analysis | Total, monthly and category-wise expenditure; average per expense, per day and per month; median; month-on-month change |
| Extremes | Highest and lowest expense, overall and per month |
| Sorting | Sort by date, amount, category, description or ID, ascending or descending |
| Records | Search by description, delete with confirmation |
| Storage | CSV file with safe (atomic) saving; invalid rows are skipped on load |
| Charts | Bar chart, donut-style pie chart, line plot, histogram (saved as PNG) |
| Reports | Export a text summary to the `reports` folder (terminal interface) |
| Interfaces | Browser dashboard (Flask) and menu-driven terminal application |
| Validation | Rejects malformed or future dates, non-numeric, zero, negative or oversized amounts, unknown categories, empty descriptions |

## Project structure

```
expense_tracker/
    app.py                web interface (Flask), run in a browser
    main.py               terminal interface entry point
    templates/            HTML pages for the web interface
    static/style.css      web interface styling
    requirements.txt
    data/expenses.csv     stored records
    reports/              generated charts and text reports
    scripts/seed_data.py  creates sample data for demonstration
    src/
        config.py         paths, categories, constants
        validators.py     input parsing and validation
        storage.py        reading, writing, adding, deleting records
        analysis.py       Pandas calculations
        report.py         text tables and reports
        charts.py         Matplotlib charts
        cli.py            menu and user interaction
    tests/                unit tests
```

The code is divided by responsibility: `validators`, `storage` and `analysis` contain no
user interaction, which keeps them easy to test; `cli` is the only module that prints
prompts and reads input.

## Setup in Visual Studio Code

1. Install Python 3.10 or later and the VS Code Python extension.
2. Open the `expense_tracker` folder (File > Open Folder).
3. Open a terminal (Terminal > New Terminal) and create a virtual environment:

   ```
   python -m venv .venv
   .venv\Scripts\activate          (Windows)
   source .venv/bin/activate       (macOS / Linux)
   ```

4. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Optional: load sample data to explore the reports straight away.

   ```
   python scripts/seed_data.py
   ```

6. Run the application. There are two interfaces over the same data file.

   Web interface (opens in Safari or any browser):

   ```
   python app.py
   ```

   Then open the URL printed in the terminal (defaults to http://127.0.0.1:5050 or http://127.0.0.1:5000)
   if it does not open automatically in your browser. Press Ctrl+C in the terminal to stop the server.

   Terminal interface:

   ```
   python main.py
   ```

To start with an empty tracker, delete the contents of `data/expenses.csv`.

## Running the tests

```
python -m unittest discover -s tests -t .
```

## Data format

Records are stored in `data/expenses.csv`:

```
id,date,category,amount,description
1,2026-04-12,Other,359.98,Mobile recharge
```

## Design notes

- **Pandas** holds the records in memory as a DataFrame and does all grouping,
  aggregation, filtering and sorting.
- **Saving** writes to a temporary file and then replaces the original, so an
  interruption cannot leave a half-written data file.
- **Input handling** is centralised in `validators.py`. Each prompt repeats until the
  value is valid, and typing `cancel` returns to the menu.
- **Commas** in descriptions are replaced with semicolons to keep the CSV format simple.

## Possible extensions

Monthly budgets with overspend alerts, recurring expenses, import from bank statements,
and a graphical interface using Tkinter.
