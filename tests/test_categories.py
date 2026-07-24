import unittest

from src.categories import Category


class CategoryTests(unittest.TestCase):
    def test_category_values_match_scenario_weight_keys(self):
        self.assertEqual(
            {category.value for category in Category},
            {
                "Shared Joy",
                "Reliability / Showing Up",
                "Emotional Support",
                "Practical Support",
                "Being Remembered",
                "Gestures",
            },
        )


if __name__ == "__main__":
    unittest.main()
