import json
from pathlib import Path
from typing import Any

from .categories import Category


_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

VARIANTS = {
    "full": "scenarios.json",
    "short": "scenarios_short.json",
}

_WEIGHT_TOLERANCE = 1e-6


def load_scenarios(variant: str = "full") -> list[dict[str, Any]]:
    """Load and validate the scenario set for the requested questionnaire variant."""
    key = variant.strip().lower()
    try:
        filename = VARIANTS[key]
    except KeyError:
        raise ValueError(
            f"Unknown variant {variant!r}: choose one of {sorted(VARIANTS)}"
        ) from None

    path = _DATA_DIR / filename
    with path.open(encoding="utf-8") as handle:
        scenarios = json.load(handle)

    validate_scenarios(scenarios)
    return scenarios


def validate_scenarios(scenarios: object) -> None:
    """Raise ValueError when a scenario dataset does not match the expected schema."""
    if not isinstance(scenarios, list):
        raise ValueError("Scenario data must be a JSON array.")

    for index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            raise ValueError(f"Scenario {index} must be an object.")

        text = scenario.get("text")
        weights = scenario.get("weights")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Scenario {index} must have non-empty text.")
        if not isinstance(weights, dict) or not weights:
            raise ValueError(f"Scenario {index} must have category weights.")

        total_weight = 0.0
        for category_name, weight in weights.items():
            try:
                Category(category_name)
            except ValueError:
                raise ValueError(
                    f"Scenario {index} has an unknown category: {category_name!r}"
                ) from None
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Scenario {index} has a non-numeric weight for {category_name!r}."
                )
            total_weight += weight

        if abs(total_weight - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(f"Scenario {index} weights must sum to 1.0.")
