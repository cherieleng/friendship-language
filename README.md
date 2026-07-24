# Friendship Language

A friendship-preference questionnaire that explores the dynamics that make close friendships feel meaningful. It collects 1–5 ratings for 40 scenarios, calculates deterministic category scores, and presents a ranked, human-readable summary.

## Categories

- Shared Joy
- Reliability / Showing Up
- Emotional Support
- Practical Support
- Being Remembered
- Gestures

## Project structure

```text
friendship-language/
├── README.md
└── src/
    ├── scenarios.json
    ├── calculator.py
    ├── questionnaire.py
    └── sample_output.md
```

`src/scenarios.json` is the source of truth for the questionnaire. Each scenario provides display text and one or more category weights, which sum to `1.0`. The Python modules are intentionally empty placeholders for the questionnaire flow and scoring implementation.

## Questionnaire behavior

- Show one randomly selected unused scenario at a time, until all 40 have been answered.
- Ask: “How meaningful would this be to you in a close friendship?”
- Use a 1–5 scale from *Not meaningful* to *Extremely meaningful*.
- Normalize each category against its total possible weighted points, then display ranked percentage scores.

Scores describe preferred friendship dynamics, not personality traits, abilities, or moral judgments.
