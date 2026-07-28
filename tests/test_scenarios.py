import unittest

from src.scenarios import load_scenarios


class LoadScenariosTests(unittest.TestCase):
    def test_loads_the_full_dataset_by_default(self):
        scenarios = load_scenarios()

        self.assertEqual(len(scenarios), 40)
        self.assertTrue(all({"text", "weights"} <= scenario.keys() for scenario in scenarios))

    def test_loads_the_short_dataset_by_variant(self):
        scenarios = load_scenarios(" SHORT ")

        self.assertEqual(len(scenarios), 25)
        for scenario in scenarios:
            self.assertAlmostEqual(sum(scenario["weights"].values()), 1.0)

    def test_rejects_unknown_variants(self):
        with self.assertRaisesRegex(ValueError, "Unknown variant"):
            load_scenarios("mini")


if __name__ == "__main__":
    unittest.main()
