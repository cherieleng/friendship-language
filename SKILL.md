---
name: friendship-language
description: Administer a friendship-preference questionnaire, calculate normalized category scores, and present a warm interpretation. Use when a user asks to explore which friendship dynamics feel meaningful to them or to run the Friendship Language Analysis.
metadata:
  version: 2.1.0
  author: Cherie Leng (Cold)
  tags: [questionnaire, friendship, self-reflection, scoring, localized]
allowed-tools:
  - Read
  - Bash(python3:*)
---

# Friendship Language Analysis

Use this analysis only to describe a user's preferred friendship dynamics. Do not infer personality traits, abilities, morality, or diagnoses.

## Language and Localization

- Use `zh_CN` when the user is communicating in Simplified Chinese.
- Use `en_US` when the user is communicating in English or when no supported locale is clear.
- For any other language, use the `en_US` templates and respond naturally in the user's language where possible.
- Use localized user-facing text from the template files.
- Prefer natural localization over literal translation.

## Run the questionnaire

1. Decide the variant: ask whether the user would like the full (40 questions) or a shorter (25 questions) version; default to `"full"` if they have no preference.
2. Load the scenarios with `load_scenarios(variant)` from `src/scenarios.py`.
3. Create `Questionnaire(scenarios)` from `src/questionnaire.py`.
4. Give a warm, two- to three-sentence introduction: 
  - explain the purpose
  - say there are no right or wrong answers
  - avoid presenting it as a personality test. 
  - briefly set expectations that this is a set of short scenarios rated one at a time.
  - Refer to `templates/{locale}/sample_opening.md` as the opening-message template.
5. Until `questionnaire.is_complete` is true:
  - call `next_question()` once
  - render `templates/{locale}/question_format.md`, replacing its `questionnaire.question_number`, `questionnaire.total_questions`, and `scenario["text"]` placeholders.
  - call `record_response(rating)` and collect user rating before selecting another scenario.
6. Call `calculate_scores(questionnaire.selected_scenarios, questionnaire.responses)` from `src/calculator.py` after the final response.

## Question Display Rules

- `questionnaire.question_number` represents the current displayed question number.
- `questionnaire.total_questions` represents the total number of questions in the questionnaire.
- Do not use scenario IDs or dataset numbering as progress indicators.
- Do not reveal scenario categories, weights, internal tracking, or scoring calculations while asking questions.

## Use the Python interfaces

- Scenarios are JSON dictionaries with `text` and `weights` keys. Weight keys are category-name strings and weights are decimals that sum to `1.0`.
- `Questionnaire` owns selection state, progress, and responses. Do not manually maintain an `asked` set.
- `calculate_scores` accepts the selected scenario dictionaries and their 1–5 responses. It returns `{Category: percentage}`; use `category.value` as the source key.

## Present results

Use `templates/{locale}/sample_output.md` as the result-layout reference.
Get all source key to category label mappings from `templates/{locale}/categories.json`.

Sort categories by descending score. For each category, show its label, a ten-slot bar, and its actual rounded percentage. Fill the bar with `round(percentage / 10)` `█` blocks and use `░` for the remainder.

Then give a short, nuanced interpretation covering the top needs, how closeness may be experienced, and friendships likely to feel fulfilling. Frame lower scores as less central, not unimportant or disliked.

End with: `Friendship Language v2 — Created by Cold`.
