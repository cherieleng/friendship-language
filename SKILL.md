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

Run all commands with `python3` from the repository root. The run is 2 commands with the conversation in between (see steps 3 and 5) - do not keep a Python process alive between questions, and do not re-run `plan`.

1. Decide the variant: ask whether the user would like the full (40 questions) or a short (25 questions) version; default to `"full"` if they have no preference.
2. Give a warm, two- to three-sentence introduction: 
  - explain the purpose
  - say there are no right or wrong answers
  - avoid presenting it as a personality test. 
  - briefly set expectations that this is a set of short scenarios rated one at a time.
  - Refer to `templates/{locale}/sample_opening.md` as the opening-message template.
3. Run `python3 -m src.cli plan --variant <full|short>` once. It prints one row per question as `position <tab> id <tab> text`. This fixed order is the record of what to ask; keep the `id` for each row for step 5.
4. Ask the scenarios in the printed order, one at a time:
  - render `templates/{locale}/question_format.md`, using the row's `position` for `questionnaire.question_number`, the printed `total` for `questionnaire.total_questions`, the row's `text` for `scenario["text"]`.
  - collect the user's 1-5 rating before showing the next scenario.
5. After the final rating, run `python3 -m src.cli score --variant <full|short> --locale <locale> --answers <id0=rating0,id1=rating1,...>`, pairing each row's `id` with the rating the user gave it (order does not matter). It prints the finished result block.

## Question Display Rules

- `questionnaire.question_number` represents the current displayed question number.
- `questionnaire.total_questions` represents the total number of questions in the questionnaire.
- Show the user the `position` as ("question {x} of {total}"); never show the `id` or dataset numbering as a progress indicator.
- Do not reveal scenario categories, weights, internal tracking, or scoring calculations while asking questions.

## Use the Python interfaces

- Scenarios are JSON dictionaries with `text` and `weights` keys. Weight keys are category-name strings and weights are decimals that sum to `1.0`. You don't need to read the files directly.
- `plan` and `score` are the only interface you need; selection, scoring, and bar rendering all happen inside them. You do not import or drive `Questionnaire` yourself.
- `score` already sorts categories by descending score, applies the localized label from `templates/{locale}/categories.json`, and renders each ten-slot bar. Do not recompute the percentages or redraw bars by hand.

## Present results

Use `templates/{locale}/sample_output.md` as the result-layout reference.
Get all source key to category label mappings from `templates/{locale}/categories.json`.

Sort categories by descending score. For each category, show its label, a ten-slot bar, and its actual rounded percentage. Fill the bar with `round(percentage / 10)` `█` blocks and use `░` for the remainder.

Then give a short, nuanced interpretation covering the top needs, how closeness may be experienced, and friendships likely to feel fulfilling. Frame lower scores as less central, not unimportant or disliked.

End with: `Friendship Language v2 — Created by Cold`.
