"""
Unit tests for the friendship-language CLI module.

Adjust MODULE_PATH below to match where this file actually lives in your
package (e.g. "friendship_language.cli" or "myproject.cli"). All patches
use MODULE_PATH so they patch names as looked up inside that module.

Assumes the _cmd_score regression has been fixed, i.e. it calls:
    answers = _parse_answers(args.answers, len(scenarios))
before checking `if not answers:`.
"""
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, patch

from src import cli

MODULE_PATH = "src.cli"

class TestParseAnswers(unittest.TestCase):
    def test_parses_valid_pairs(self):
        result = cli._parse_answers("0=3,1=5,2=1", total=3)
        self.assertEqual(result, {0: 3, 1: 5, 2: 1})

    def test_ignores_blank_chunks_and_whitespace(self):
        result = cli._parse_answers(" 0=3 , , 1=4 ", total=2)
        self.assertEqual(result, {0: 3, 1: 4})

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(cli._parse_answers("", total=5), {})

    def test_missing_equals_raises(self):
        with self.assertRaisesRegex(ValueError, "Expected id=rating"):
            cli._parse_answers("0-3", total=5)

    def test_non_integer_id_raises(self):
        with self.assertRaisesRegex(ValueError, "must be integers"):
            cli._parse_answers("a=3", total=5)

    def test_non_integer_rating_raises(self):
        with self.assertRaisesRegex(ValueError, "must be integers"):
            cli._parse_answers("0=x", total=5)

    def test_id_out_of_range_raises(self):
        with self.assertRaisesRegex(ValueError, "Invalid question id"):
            cli._parse_answers("5=3", total=3)

    def test_negative_id_raises(self):
        with self.assertRaisesRegex(ValueError, "Invalid question id"):
            cli._parse_answers("-1=3", total=3)

    def test_rating_below_range_raises(self):
        with self.assertRaisesRegex(ValueError, "Invalid rating id"):
            cli._parse_answers("0=0", total=3)

    def test_rating_above_range_raises(self):
        with self.assertRaisesRegex(ValueError, "Invalid rating id"):
            cli._parse_answers("0=6", total=3)

    def test_rating_boundaries_are_inclusive(self):
        result = cli._parse_answers("0=1,1=5", total=2)
        self.assertEqual(result, {0: 1, 1: 5})

    def test_duplicate_id_keeps_latest_and_warns(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = cli._parse_answers("0=1,0=4", total=1)
        self.assertEqual(result, {0: 4})
        self.assertIn("more than once", buf.getvalue())


class TestRenderBar(unittest.TestCase):
    def test_zero_percent(self):
        self.assertEqual(cli._render_bar(0), "░" * cli._BAR_SLOTS)

    def test_hundred_percent(self):
        self.assertEqual(cli._render_bar(100), "█" * cli._BAR_SLOTS)

    def test_fifty_percent(self):
        bar = cli._render_bar(50)
        self.assertEqual(bar.count("█"), 5)
        self.assertEqual(bar.count("░"), 5)

    def test_clamped_below_zero(self):
        self.assertEqual(cli._render_bar(-20), "░" * cli._BAR_SLOTS)

    def test_clamped_above_hundred(self):
        self.assertEqual(cli._render_bar(150), "█" * cli._BAR_SLOTS)

    def test_length_always_bar_slots(self):
        for pct in (0, 7, 33, 50, 91, 100):
            self.assertEqual(len(cli._render_bar(pct)), cli._BAR_SLOTS)


class TestLoadLabels(unittest.TestCase):
    @patch(f"{MODULE_PATH}._TEMPLATE_DIR")
    def test_reads_and_parses_json(self, mock_dir):
        fake_path = MagicMock()
        fake_path.read_text.return_value = '{"warmth": "Warmth"}'
        mock_dir.__truediv__.return_value.__truediv__.return_value = fake_path

        result = cli._load_labels("en_US")

        self.assertEqual(result, {"warmth": "Warmth"})
        fake_path.read_text.assert_called_once_with(encoding="utf-8")

    @patch(f"{MODULE_PATH}._TEMPLATE_DIR")
    def test_missing_file_propagates(self, mock_dir):
        fake_path = MagicMock()
        fake_path.read_text.side_effect = FileNotFoundError("no such file")
        mock_dir.__truediv__.return_value.__truediv__.return_value = fake_path

        with self.assertRaises(FileNotFoundError):
            cli._load_labels("xx_XX")


class TestCmdPlan(unittest.TestCase):
    @patch(f"{MODULE_PATH}.select_all")
    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_prints_position_id_text_in_order(self, mock_load, mock_select):
        scenarios = {0: {"text": "first"}, 1: {"text": "second"}}
        mock_load.return_value = scenarios
        mock_select.return_value = [1, 0]  # deliberately shuffled order

        args = MagicMock(variant="full")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli._cmd_plan(args)

        self.assertEqual(rc, 0)
        lines = [l for l in buf.getvalue().splitlines() if not l.startswith("#")]
        self.assertEqual(lines, ["1\t1\tsecond", "2\t0\tfirst"])
        mock_load.assert_called_once_with("full")

    @patch(f"{MODULE_PATH}.select_all")
    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_empty_order_prints_only_header(self, mock_load, mock_select):
        mock_load.return_value = {}
        mock_select.return_value = []

        args = MagicMock(variant="short")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli._cmd_plan(args)

        self.assertEqual(rc, 0)
        body_lines = [l for l in buf.getvalue().splitlines() if not l.startswith("#")]
        self.assertEqual(body_lines, [])


class TestCmdScore(unittest.TestCase):
    @patch(f"{MODULE_PATH}._load_labels")
    @patch(f"{MODULE_PATH}.calculate_scores")
    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_happy_path_renders_ranked_bars(self, mock_load, mock_calc, mock_labels):
        scenarios = {0: {"text": "a"}, 1: {"text": "b"}}
        mock_load.return_value = scenarios

        warmth = MagicMock(value="warmth")
        trust = MagicMock(value="trust")
        mock_calc.return_value = {warmth: 40, trust: 90}
        mock_labels.return_value = {"warmth": "Warmth", "trust": "Trust"}

        args = MagicMock(variant="full", locale="en_US", answers="0=5,1=2")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli._cmd_score(args)

        self.assertEqual(rc, 0)
        output = buf.getvalue()
        # higher percentage (Trust, 90) should be ranked before Warmth (40)
        self.assertLess(output.index("Trust"), output.index("Warmth"))
        self.assertIn("90%", output)
        self.assertIn("40%", output)
        mock_calc.assert_called_once()

    @patch(f"{MODULE_PATH}._load_labels")
    @patch(f"{MODULE_PATH}.calculate_scores")
    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_unknown_category_falls_back_to_raw_value(self, mock_load, mock_calc, mock_labels):
        scenarios = {0: {"text": "a"}}
        mock_load.return_value = scenarios
        mystery = MagicMock(value="mystery")
        mock_calc.return_value = {mystery: 10}
        mock_labels.return_value = {}  # no label for "mystery"

        args = MagicMock(variant="full", locale="en_US", answers="0=3")
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli._cmd_score(args)

        self.assertIn("mystery", buf.getvalue())

    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_no_answers_raises_value_error(self, mock_load):
        mock_load.return_value = {0: {"text": "a"}}
        args = MagicMock(variant="full", locale="en_US", answers="")

        with self.assertRaisesRegex(ValueError, "No answers provided"):
            cli._cmd_score(args)

    @patch(f"{MODULE_PATH}.load_scenarios")
    def test_invalid_answers_string_propagates_parse_error(self, mock_load):
        mock_load.return_value = {0: {"text": "a"}}
        args = MagicMock(variant="full", locale="en_US", answers="oops")

        with self.assertRaises(ValueError):
            cli._cmd_score(args)


class TestMainWiring(unittest.TestCase):
    @patch(f"{MODULE_PATH}._cmd_plan", return_value=0)
    def test_plan_subcommand_dispatches(self, mock_cmd):
        rc = cli.main(["plan", "--variant", "short"])
        self.assertEqual(rc, 0)
        mock_cmd.assert_called_once()
        called_args = mock_cmd.call_args[0][0]
        self.assertEqual(called_args.variant, "short")

    @patch(f"{MODULE_PATH}._cmd_score", return_value=0)
    def test_score_subcommand_dispatches_with_defaults(self, mock_cmd):
        rc = cli.main(["score", "--answers", "0=3"])
        self.assertEqual(rc, 0)
        called_args = mock_cmd.call_args[0][0]
        self.assertEqual(called_args.locale, "en_US")
        self.assertEqual(called_args.variant, "full")
        self.assertEqual(called_args.answers, "0=3")

    def test_score_requires_answers_flag(self):
        buf = io.StringIO()
        with redirect_stderr(buf), self.assertRaises(SystemExit):
            cli.main(["score"])

    def test_no_subcommand_errors(self):
        buf = io.StringIO()
        with redirect_stderr(buf), self.assertRaises(SystemExit):
            cli.main([])

    def test_invalid_variant_choice_errors(self):
        buf = io.StringIO()
        with redirect_stderr(buf), self.assertRaises(SystemExit):
            cli.main(["plan", "--variant", "not-a-real-variant"])

    @patch(f"{MODULE_PATH}._cmd_plan", side_effect=ValueError("boom"))
    def test_value_error_from_command_is_caught_and_returns_2(self, mock_cmd):
        buf = io.StringIO()
        with redirect_stderr(buf):
            rc = cli.main(["plan"])
        self.assertEqual(rc, 2)
        self.assertIn("error: boom", buf.getvalue())

    @patch(f"{MODULE_PATH}._cmd_score", side_effect=FileNotFoundError("missing labels"))
    def test_file_not_found_from_command_is_caught_and_returns_2(self, mock_cmd):
        buf = io.StringIO()
        with redirect_stderr(buf):
            rc = cli.main(["score", "--answers", "0=3"])
        self.assertEqual(rc, 2)
        self.assertIn("error: missing labels", buf.getvalue())


if __name__ == "__main__":
    unittest.main()