---
name: friendship-language
description: Administer a friendship-preference questionnaire, calculate normalized category scores, and present a warm interpretation. Use when a user asks to explore which friendship dynamics feel meaningful to them or to run the Friendship Compatibility Analysis.
---

# Friendship Compatibility Analysis

Use this analysis only to describe a user's preferred friendship dynamics. Do not infer personality traits, abilities, morality, or diagnoses.

## Run the questionnaire

1. Load `src/scenarios.json` with `json.load`.
2. Create `Questionnaire(scenarios)` from `src/questionnaire.py`.
3. Give a warm, two- to three-sentence introduction: explain the purpose, say there are no right or wrong answers, and avoid presenting it as a personality test. Refer to `src/sample_opening.md` as the opening-message template.
4. Until `questionnaire.is_complete` is true, call `next_question()` once, then display `Question {questionnaire.question_number} of {questionnaire.total_questions}` with its `text` and the rating scale below. Call `record_response(rating)` before selecting another scenario.
5. Call `calculate_scores(questionnaire.selected_scenarios, questionnaire.responses)` from `src/calculator.py` after the final response.

Display with every scenario:


```text
Question {questionnaire.question_number} of {questionnaire.total_questions}

How meaningful would this be to you in a close friendship?

{ Insert scenario text here }

1 = Not meaningful
2 = Slightly meaningful
3 = Moderately meaningful
4 = Very meaningful
5 = Extremely meaningful
```

Do not reveal scenario categories, weights, internal tracking, or scoring calculations while asking questions.

## Use the Python interfaces

- Scenarios are JSON dictionaries with `text` and `weights` keys. Weight keys are category-name strings and weights are decimals that sum to `1.0`.
- `Questionnaire` owns selection state, progress, and responses. Do not manually maintain an `asked` set.
- `calculate_scores` accepts the selected scenario dictionaries and their 1–5 responses. It returns `{Category: percentage}`; use `category.value` for display labels.

## Present results

Use `src/sample_output.md` as the result-layout reference.

Sort categories by descending score. For each category, show its label, a ten-slot bar, and its actual rounded percentage. Fill the bar with `round(percentage / 10)` `█` blocks and use `░` for the remainder.

Then give a short, nuanced interpretation covering the top needs, how closeness may be experienced, and friendships likely to feel fulfilling. Frame lower scores as less central, not unimportant or disliked.

End with: `Friendship Compatibility Analysis v2 — Created by Cold`.