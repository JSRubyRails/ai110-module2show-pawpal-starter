"""PawPal+ core system.

Classes implemented from diagrams/uml.mmd: data objects (Task, Pet, Owner,
ScheduledTask, Plan) plus the Scheduler engine that turns tasks + constraints
into an ordered daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta

# Priority labels mapped to a sortable rank (higher = more important).
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}


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
        return self.recurrence != "none"

    def priority_rank(self) -> int:
        """Map priority to a sortable number (higher = more important)."""
        return PRIORITY_RANKS.get(self.priority.lower(), PRIORITY_RANKS["medium"])


@dataclass
class Pet:
    """An animal being cared for."""

    name: str
    species: str  # dog | cat | other
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet by its index in the task list."""
        if 0 <= task_id < len(self.tasks):
            del self.tasks[task_id]
        else:
            raise IndexError(f"No task at index {task_id}")

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks


@dataclass
class Owner:
    """The person planning care and their preferences."""

    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_preference(self, key: str, value) -> None:
        """Store a planning constraint/preference."""
        self.preferences[key] = value

    def get_preference(self, key: str):
        """Look up a stored preference (None if unset)."""
        return self.preferences.get(key)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)


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
        """Append a scheduled task and accumulate total time."""
        self.entries.append(scheduled_task)
        self.total_minutes += scheduled_task.task.duration_minutes

    def explain(self) -> str:
        """Explain why each task was chosen and ordered."""
        lines = []
        for entry in self.entries:
            t = entry.task
            lines.append(
                f"{entry.start_time:%H:%M} — {t.title} ({t.duration_minutes} min) "
                f"[priority: {t.priority}]"
            )
        if self.skipped:
            skipped_titles = ", ".join(t.title for t in self.skipped)
            lines.append(
                f"Skipped (not enough time): {skipped_titles}"
            )
        if not self.entries:
            return "No tasks could be scheduled within the available time."
        header = (
            f"Scheduled {len(self.entries)} task(s) using {self.total_minutes} min, "
            "ordered by priority then placed in order:"
        )
        return header + "\n" + "\n".join(lines)

    def to_table(self) -> list[dict]:
        """Return rows suitable for display (e.g. st.table)."""
        return [
            {
                "start": f"{e.start_time:%H:%M}",
                "end": f"{e.end_time:%H:%M}",
                "task": e.task.title,
                "duration_minutes": e.task.duration_minutes,
                "priority": e.task.priority,
            }
            for e in self.entries
        ]


class Scheduler:
    """Turns tasks + constraints into an ordered Plan."""

    def __init__(self, available_minutes: int, start_time: time = time(8, 0)) -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time

    def build_plan(self, tasks: list[Task]) -> Plan:
        """Sort by priority, then greedily place tasks that fit the time budget."""
        plan = Plan()
        remaining = self.available_minutes
        cursor = self._to_datetime(self.start_time)

        for task in self.sort_by_priority(tasks):
            if self.fits(task, remaining):
                end = cursor + timedelta(minutes=task.duration_minutes)
                plan.add_entry(
                    ScheduledTask(
                        task=task,
                        start_time=cursor.time(),
                        end_time=end.time(),
                    )
                )
                cursor = end
                remaining -= task.duration_minutes
            else:
                plan.skipped.append(task)

        return plan

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Order by priority (high first), then shorter tasks first as a tiebreaker."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_rank(), t.duration_minutes),
        )

    def fits(self, task: Task, remaining_time: int) -> bool:
        """Return True if the task fits in the remaining time budget."""
        return task.duration_minutes <= remaining_time

    def resolve_conflicts(self, scheduled: list[ScheduledTask]) -> None:
        """Push overlapping slots later so no two tasks share a time range.

        Mutates the list in place, assuming it is already in start-time order.
        """
        for i in range(1, len(scheduled)):
            prev, curr = scheduled[i - 1], scheduled[i]
            if curr.start_time < prev.end_time:
                duration = self._minutes_between(curr.start_time, curr.end_time)
                new_start = self._to_datetime(prev.end_time)
                new_end = new_start + timedelta(minutes=duration)
                curr.start_time = new_start.time()
                curr.end_time = new_end.time()

    @staticmethod
    def _to_datetime(t: time) -> datetime:
        """Anchor a time to an arbitrary date so timedelta math works."""
        return datetime(2000, 1, 1, t.hour, t.minute)

    @classmethod
    def _minutes_between(cls, start: time, end: time) -> int:
        delta = cls._to_datetime(end) - cls._to_datetime(start)
        return int(delta.total_seconds() // 60)
