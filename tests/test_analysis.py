import tempfile
import unittest
from datetime import date
from pathlib import Path

import pandas as pd

from src import analysis, storage


def sample() -> pd.DataFrame:
    df = storage.empty_frame()
    entries = [
        (date(2026, 1, 5), "Food", 200.0, "Groceries"),
        (date(2026, 1, 20), "Travel", 500.0, "Train ticket"),
        (date(2026, 2, 3), "Food", 100.0, "Lunch"),
        (date(2026, 2, 14), "Shopping", 1200.0, "Shoes"),
    ]
    for entry in entries:
        df = storage.add_expense(df, *entry)
    return df


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.df = sample()

    def test_total_and_average(self):
        self.assertEqual(analysis.total_spent(self.df), 2000.0)
        stats = analysis.average_stats(self.df)
        self.assertEqual(stats["per_expense"], 500.0)
        self.assertEqual(stats["per_month"], 1000.0)

    def test_monthly_and_category_totals(self):
        monthly = analysis.monthly_totals(self.df)
        self.assertEqual(list(monthly.values), [700.0, 1300.0])
        self.assertEqual(analysis.category_totals(self.df)["Food"], 300.0)

    def test_extremes(self):
        high, low = analysis.extremes(self.df)
        self.assertEqual(high.amount, 1200.0)
        self.assertEqual(low.amount, 100.0)

    def test_sorting(self):
        ordered = analysis.sort_expenses(self.df, "amount", ascending=False)
        self.assertEqual(list(ordered["amount"]), [1200.0, 500.0, 200.0, 100.0])
        with self.assertRaises(ValueError):
            analysis.sort_expenses(self.df, "colour")

    def test_filter_and_search(self):
        self.assertEqual(len(analysis.filter_month(self.df, 2026, 2)), 2)
        self.assertEqual(len(analysis.search_expenses(self.df, "lunch")), 1)

    def test_month_over_month(self):
        self.assertAlmostEqual(analysis.month_over_month(self.df), 85.714, places=2)

    def test_empty_data(self):
        empty = storage.empty_frame()
        self.assertEqual(analysis.total_spent(empty), 0.0)
        self.assertEqual(analysis.extremes(empty), (None, None))
        self.assertEqual(analysis.average_stats(empty)["per_day"], 0.0)


class StorageTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "expenses.csv"
            storage.save_expenses(sample(), path)
            loaded, skipped = storage.load_expenses(path)
            self.assertEqual(skipped, 0)
            self.assertEqual(len(loaded), 4)
            self.assertEqual(loaded["amount"].sum(), 2000.0)

    def test_bad_rows_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "expenses.csv"
            path.write_text(
                "id,date,category,amount,description\n"
                "1,2026-01-05,Food,200.00,Groceries\n"
                "2,not-a-date,Food,50.00,Broken\n"
                "3,2026-01-06,Food,-10.00,Negative\n",
                encoding="utf-8",
            )
            loaded, skipped = storage.load_expenses(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(skipped, 2)

    def test_missing_file_gives_empty_frame(self):
        loaded, skipped = storage.load_expenses(Path("does_not_exist.csv"))
        self.assertTrue(loaded.empty)

    def test_delete(self):
        df, removed = storage.delete_expense(sample(), 2)
        self.assertTrue(removed)
        self.assertEqual(len(df), 3)
        _, removed = storage.delete_expense(df, 99)
        self.assertFalse(removed)


if __name__ == "__main__":
    unittest.main()
