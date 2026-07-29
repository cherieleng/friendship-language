import argparse
import json
import sys
from pathlib import Path

from .calculator import calculate_scores
from .questionnaire import select_all
from .scenarios import VARIANTS, load_scenarios

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_BAR_SLOTS = 10

def _load_labels(locale: str) -> dict[str, str]:
    """Map each category source key to its localized display label."""
    path = _TEMPLATE_DIR / locale / "categories.json"
    return json.loads(path.read_text(encoding="utf-8"))

def _render_bar(percentage: int) -> str:
    filled = round(percentage / (100/_BAR_SLOTS))
    filled = max(0, min(_BAR_SLOTS, filled))
    return "█"*filled + "░"*(_BAR_SLOTS - filled)

def _parse_answers(raw: str, total: int) -> dict[int, int]:
    """Parse `id=rating` pairs into {dataset_id: rating}, ids 0 based, ratings 1-5"""
    answers: dict[int, int] = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(f"Expected id=rating, got {chunk!r}.")
        id_text, rating_text = chunk.split("=", 1)
        try: 
            dataset_id = int(id_text)
            rating = int(rating_text)
        except ValueError:
            raise ValueError(f"id and rating must be integers in {chunk!r}.") from None
        if not 0 <= dataset_id < total:
            raise ValueError("Invalid question id.")
        if not 1 <= rating <= 5:
            raise ValueError("Invalid rating id.")
        if dataset_id in answers:
            print(f"Warning: Question {dataset_id} was answered more than once, using latest value")
        answers[dataset_id] = rating
    return answers
        
def _add_variant(sub_parser: argparse.ArgumentParser) -> None:
    sub_parser.add_argument(
        "--variant",
        default="full",
        choices=sorted(VARIANTS),
        help="Questionnaire size (default: full)."
    )
    
def _cmd_plan(args: argparse.Namespace) -> int:
    scenarios = load_scenarios(args.variant)
    order = select_all(scenarios)
    print(f"# variant={args.variant} total={len(order)}")
    print("# columns: position <tab> id <tab> text")
    print("# ask in this order; show 'position of total' to the user, never the id")
    for position, dataset_index in enumerate(order, start=1):
        # position: the order to ask question in, shown to the user
        # id (dataset_index): the scenario's 0-indexed place in the original dataset. Stable across runs. Not shown to the user.
        print(f"{position}\t{dataset_index}\t{scenarios[dataset_index]['text']}")
    return 0
    
def _cmd_score(args: argparse.Namespace) -> int:
    scenarios = load_scenarios(args.variant)
    answers = _parse_answers(args.answers, len(scenarios))
    if not answers:
        raise ValueError("No answers provided.")
    
    selected = [scenarios[dataset_id] for dataset_id in answers]
    ratings = list(answers.values())
    scores = calculate_scores(selected, ratings)

    labels = _load_labels(args.locale)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    lines: list[str] = []
    for category, percentage in ranked:
        label = labels.get(category.value, category.value)
        lines.append(label)
        lines.append(f"{_render_bar(percentage)} {percentage}%")
        lines.append("")
    print("\n".join(lines).rstrip())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="friendship-language")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan",  help="Select and print the ordered questions.")
    _add_variant(plan)
    plan.set_defaults(func=_cmd_plan)
    score = sub.add_parser("score", help="Render the result block from id=rating answers.")
    _add_variant(score)
    score.add_argument("--locale", default="en_US")
    score.add_argument("--answers", required=True, help="Comma-separated id=rating pairs.")
    score.set_defaults(func=_cmd_score)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    
if __name__ == "__main__":
    sys.exit(main())