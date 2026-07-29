import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Questionnaire:
    """Manage scenario selection, progress, and responses for one questionnaire run."""

    scenarios: Sequence[dict[str, Any]]
    _asked_indices: set[int] = field(default_factory=set, init=False)
    _selected_indices: list[int] = field(default_factory=list, init=False)
    _responses: list[int] = field(default_factory=list, init=False)
    _current_index: int | None = field(default=None, init=False)

    @property
    def total_questions(self) -> int:
        return len(self.scenarios)

    @property
    def completed_count(self) -> int:
        return len(self._responses)

    @property
    def question_number(self) -> int:
        """Return the one-based number of the scenario currently being displayed."""
        if self._current_index is None:
            raise RuntimeError("No question is currently awaiting a response.")
        return self.completed_count + 1

    @property
    def is_complete(self) -> bool:
        return self.completed_count == self.total_questions

    @property
    def selected_scenarios(self) -> list[dict[str, Any]]:
        return [self.scenarios[index] for index in self._selected_indices]

    @property
    def responses(self) -> list[int]:
        return list(self._responses)

    def next_question(self) -> dict[str, Any]:
        """Randomly select one unused scenario and mark it as in progress."""
        if self._current_index is not None:
            raise RuntimeError("Record a response before selecting another question.")
        if self.is_complete:
            raise StopIteration("All questionnaire scenarios have been answered.")

        remaining_indices = [
            index
            for index in range(self.total_questions)
            if index not in self._asked_indices
        ]
        index = random.choice(remaining_indices)
        self._asked_indices.add(index)
        self._selected_indices.append(index)
        self._current_index = index
        return self.scenarios[index]

    def record_response(self, rating: int) -> None:
        """Save the rating for the scenario currently being displayed."""
        if self._current_index is None:
            raise RuntimeError("Select a question before recording a response.")
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError("Responses must be whole-number ratings from 1 to 5.")

        self._responses.append(rating)
        self._current_index = None

def select_all(scenarios: Sequence[dict[str, Any]]) -> list[int]:
    """Return every scenario index in random order in a single call. 
    
    Batch equivalent of calling `next_question` until the questionnaire is complete, 
    for callers that must fix the whole order in single process"""
    return random.sample(range(len(scenarios)), len(scenarios))
    
def pick_question(scenarios: Sequence[dict[str, Any]], asked: set[int]) -> dict[str, Any]:
    """Select one unused scenario for callers managing their own state."""
    remaining_indices = [
        index for index in range(len(scenarios)) if index not in asked
    ]
    if not remaining_indices:
        raise StopIteration("All questionnaire scenarios have been asked.")

    index = random.choice(remaining_indices)
    asked.add(index)
    return scenarios[index]
