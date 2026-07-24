from collections.abc import Mapping, Sequence

from .categories import Category


def calculate_scores(
    scenarios: Sequence[Mapping[str, Mapping[str, float]]],
    responses: Sequence[int],
) -> dict[Category, int]:
    """Return normalized, rounded category percentages for questionnaire responses."""
    if len(scenarios) != len(responses):
        raise ValueError("Each selected scenario must have exactly one response.")

    totals = {category: 0.0 for category in Category}
    possible = {category: 0.0 for category in Category}

    for scenario, rating in zip(scenarios, responses):
        if not 1 <= rating <= 5:
            raise ValueError("Responses must be whole-number ratings from 1 to 5.")

        for category_name, weight in scenario["weights"].items():
            category = Category(category_name)
            totals[category] += rating * weight
            possible[category] += 5 * weight

    return {
        category: round(totals[category] / possible[category] * 100)
        if possible[category]
        else 0
        for category in Category
    }
