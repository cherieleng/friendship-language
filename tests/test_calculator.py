import unittest

from src.calculator import calculate_scores
from src.categories import Category


class CalculateScoresTests(unittest.TestCase):
    def test_normalizes_weighted_scores_to_whole_percentages(self):
        scenarios = [
            {"weights": {"Shared Joy": 1.0}},
            {
                "weights": {
                    "Shared Joy": 0.5,
                    "Gestures": 0.5,
                }
            },
        ]

        scores = calculate_scores(scenarios, [5, 3])

        self.assertEqual(scores[Category.SHARED_JOY], 87)
        self.assertEqual(scores[Category.GESTURES], 60)

    def test_returns_zero_for_a_category_with_no_possible_points(self):
        scores = calculate_scores(
            [{"weights": {"Shared Joy": 1.0}}],
            [5],
        )

        self.assertEqual(scores[Category.EMOTIONAL_SUPPORT], 0)

    def test_rejects_mismatched_scenarios_and_responses(self):
        with self.assertRaises(ValueError):
            calculate_scores([{"weights": {"Shared Joy": 1.0}}], [])


if __name__ == "__main__":
    unittest.main()
