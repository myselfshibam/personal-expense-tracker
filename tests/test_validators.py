import unittest
from datetime import date, timedelta

from src import validators


class DateTests(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(validators.parse_date("2025-03-14"), date(2025, 3, 14))

    def test_rejects_bad_format(self):
        for text in ["14-03-2025", "2025/03/14", "yesterday", ""]:
            with self.assertRaises(ValueError):
                validators.parse_date(text)

    def test_rejects_impossible_date(self):
        with self.assertRaises(ValueError):
            validators.parse_date("2025-02-30")

    def test_rejects_future_date(self):
        with self.assertRaises(ValueError):
            validators.parse_date((date.today() + timedelta(days=1)).isoformat())


class AmountTests(unittest.TestCase):
    def test_valid_amounts(self):
        self.assertEqual(validators.parse_amount("249.5"), 249.5)
        self.assertEqual(validators.parse_amount("1,250"), 1250.0)
        self.assertEqual(validators.parse_amount("10.456"), 10.46)

    def test_rejects_invalid_amounts(self):
        for text in ["abc", "", "0", "-5", "nan", "inf", "99999999999"]:
            with self.assertRaises(ValueError):
                validators.parse_amount(text)


class CategoryTests(unittest.TestCase):
    def test_by_number_and_name(self):
        self.assertEqual(validators.parse_category("1"), "Food")
        self.assertEqual(validators.parse_category("travel"), "Travel")

    def test_rejects_unknown(self):
        for text in ["0", "99", "Gadgets", ""]:
            with self.assertRaises(ValueError):
                validators.parse_category(text)


class OtherTests(unittest.TestCase):
    def test_description(self):
        self.assertEqual(validators.parse_description("  Lunch,  office "), "Lunch; office")
        with self.assertRaises(ValueError):
            validators.parse_description("   ")

    def test_month(self):
        self.assertEqual(validators.parse_month("2026-03"), (2026, 3))
        with self.assertRaises(ValueError):
            validators.parse_month("2026-13")


if __name__ == "__main__":
    unittest.main()
