import unittest
from unittest.mock import patch

from src.questionnaire import Questionnaire, pick_question, select_all


class PickQuestionTests(unittest.TestCase):
    def test_returns_an_unused_scenario_and_marks_it_asked(self):
        scenarios = ["first", "second", "third"]
        asked = {0}

        with patch("src.questionnaire.random.choice", return_value=2):
            question = pick_question(scenarios, asked)

        self.assertEqual(question, "third")
        self.assertEqual(asked, {0, 2})

    def test_does_not_repeat_a_question_across_a_full_run(self):
        scenarios = ["first", "second", "third"]
        asked = set()
        selected = []

        while len(asked) < len(scenarios):
            selected.append(pick_question(scenarios, asked))

        self.assertCountEqual(selected, scenarios)
        self.assertEqual(len(selected), len(set(selected)))

    def test_questionnaire_tracks_progress_and_responses(self):
        scenarios = [{"text": "first"}, {"text": "second"}]
        questionnaire = Questionnaire(scenarios)

        with patch("src.questionnaire.random.choice", side_effect=[1, 0]):
            self.assertEqual(questionnaire.next_question(), scenarios[1])
            self.assertEqual(questionnaire.question_number, 1)
            questionnaire.record_response(4)
            self.assertEqual(questionnaire.next_question(), scenarios[0])
            self.assertEqual(questionnaire.question_number, 2)
            questionnaire.record_response(5)

        self.assertTrue(questionnaire.is_complete)
        self.assertEqual(questionnaire.selected_scenarios, [scenarios[1], scenarios[0]])
        self.assertEqual(questionnaire.responses, [4, 5])

    def test_questionnaire_requires_a_response_before_the_next_question(self):
        questionnaire = Questionnaire([{"text": "only"}])
        questionnaire.next_question()

        with self.assertRaises(RuntimeError):
            questionnaire.next_question()

class SelectAllTests(unittest.TestCase):
    def test_returns_every_index_exactly_once(self):
        order = select_all(["a", "b", "c"])
        self.assertEqual(sorted(order), [0, 1, 2])

    def test_length_matches_the_scenario_count(self):
        self.assertEqual(len(select_all(list(range(25)))), 25)

    def test_empty_input_yields_empty_order(self):
        self.assertEqual(select_all([]), [])


if __name__ == "__main__":
    unittest.main()