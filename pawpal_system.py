"""PawPal+ core system.

Class skeleton generated from diagrams/uml.mmd.
Attributes are defined; method bodies are stubs to be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    """A single pet-care action to be scheduled."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk, feeding, meds, grooming, ...
    recurrence: str = "none"  # "none" | "daily" | "weekly"

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily/weekly)."""
        raise NotImplementedError

    def priority_rank(self) -> int:
        """Map priority to a sortable number (higher = more important)."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal being cared for."""

    name: str
    species: str  # dog | cat | other
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person planning care and their preferences."""

    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_preference(self, key: str, value) -> None:
        """Store a planning constraint/preference."""
        raise NotImplementedError

    def get_preference(self, key: str):
        """Look up a stored preference."""
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError


@dataclass
class ScheduledTask:
    """A task placed at a concrete time slot in a plan."""

    task: Task
    start_time: time
    end_time: time


@dataclass
class Plan:
    """The generated daily schedule a user reads."""

    entries: list[ScheduledTask] = field(default_factory=list)
    total_minutes: int = 0
    skipped: list[Task] = field(default_factory=list)

    def add_entry(self, scheduled_task: ScheduledTask) -> None:
        """Append a scheduled task to the plan."""
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why each task was chosen and ordered."""
        raise NotImplementedError

    def to_table(self) -> list[dict]:
        """Return rows suitable for display (e.g. st.table)."""
        raise NotImplementedError


class Scheduler:
    """Turns tasks + constraints into an ordered Plan."""

    def __init__(self, available_minutes: int, start_time: time = time(8, 0)) -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time

    def build_plan(self, tasks: list[Task]) -> Plan:
        """Sort, filter, and place tasks into a Plan."""
        raise NotImplementedError

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority (and any tiebreakers)."""
        raise NotImplementedError

    def fits(self, task: Task, remaining_time: int) -> bool:
        """Return True if the task fits in the remaining time budget."""
        raise NotImplementedError

    def resolve_conflicts(self, scheduled: list[ScheduledTask]) -> None:
        """Adjust overlapping time slots."""
        raise NotImplementedError