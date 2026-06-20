"""PawPal+ core system.

Classes implemented from diagrams/uml.mmd: data objects (Task, Pet, Owner,
ScheduledTask, Plan) plus the Scheduler engine that turns tasks + constraints
into an ordered daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# Priority labels mapped to a sortable rank (higher = more important).
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}

# How far ahead each recurrence rule schedules the next occurrence.
# timedelta does the calendar math (month/year/leap-year rollover) for us.
RECURRENCE_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),  # weeks=1 is exactly 7 days
}


@dataclass
class Task:
    """A single pet-care action to be scheduled."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk, feeding, meds, grooming, ...
    recurrence: str = "none"  # "none" | "daily" | "weekly"
    status: str = "pending"  # "pending" | "complete"
    due_date: date | None = None

    def mark_complete(self) -> Task | None:
        """Mark this task as done; return the next occurrence if it recurs.

        For "daily"/"weekly" tasks this creates a fresh pending Task due on the
        next occurrence and returns it. Returns None for non-recurring tasks.
        The caller is responsible for adding the returned task to its pet.
        """
        self.status = "complete"
        return self.next_occurrence()

    def next_occurrence(self, *, from_date: date | None = None) -> Task | None:
        """Build the next pending instance of a recurring task (None if it doesn't recur).

        The next due date is the current due_date advanced by the recurrence
        interval; if this task has no due_date, it's based on `from_date`
        (default: today). date + timedelta handles month/year rollover for us.
        """
        delta = RECURRENCE_DELTAS.get(self.recurrence)
        if delta is None:
            return None  # "none" or an unknown recurrence: nothing to schedule
        base = self.due_date or from_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            recurrence=self.recurrence,
            status="pending",
            due_date=base + delta,
        )

    def is_complete(self) -> bool:
        """Return True if this task has been completed."""
        return self.status == "complete"

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

    def complete_task(self, task_id: int) -> Task | None:
        """Mark a task complete and auto-add its next occurrence if it recurs.

        Returns the newly created follow-up task, or None if it doesn't recur.
        """
        if not 0 <= task_id < len(self.tasks):
            raise IndexError(f"No task at index {task_id}")
        follow_up = self.tasks[task_id].mark_complete()
        if follow_up is not None:
            self.tasks.append(follow_up)
        return follow_up


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

    def find_tasks(
        self, *, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return tasks across all pets, optionally filtered by status and/or pet.

        Pass `completed=True`/`False` to filter by completion status, and/or
        `pet_name` to limit to one pet (case-insensitive). Omit a filter to
        ignore it; omitting both returns every task.
        """
        results = []
        for pet in self.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.is_complete() != completed:
                    continue
                results.append(task)
        return results


@dataclass
class ScheduledTask:
    """A task placed at a concrete time slot in a plan."""

    task: Task
    start_time: time
    end_time: time
    pet_name: str = ""  # which pet this slot belongs to (for conflict messages)


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
        """Set the daily time budget and the time of day planning starts."""
        self.available_minutes = available_minutes
        self.start_time = start_time

    def build_plan(self, tasks: list[Task], pet_name: str = "") -> Plan:
        """Sort by priority, then greedily place tasks that fit the time budget.

        Pass `pet_name` to tag each slot with its owner so conflict warnings can
        say which pet a task belongs to.
        """
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
                        pet_name=pet_name,
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

    def sort_by_time(self, scheduled: list[ScheduledTask]) -> list[ScheduledTask]:
        """Order scheduled tasks chronologically by start time.

        Useful before resolve_conflicts, which assumes start-time order.
        """
        return sorted(scheduled, key=lambda st: st.start_time)

    def fits(self, task: Task, remaining_time: int) -> bool:
        """Return True if the task fits in the remaining time budget."""
        return task.duration_minutes <= remaining_time

    def detect_conflicts(self, scheduled: list[ScheduledTask]) -> list[str]:
        """Return a warning string for each overlapping pair of time slots.

        Lightweight, non-destructive conflict detection: it never mutates the
        schedule and never raises. It compares every pair of entries and flags
        any whose time ranges overlap (two tasks share part of the same slot),
        whether they belong to the same pet or different pets. Returns an empty
        list when there are no conflicts.
        """
        warnings = []
        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                # Half-open overlap test: a starts before b ends AND b starts before a ends.
                if a.start_time < b.end_time and b.start_time < a.end_time:
                    warnings.append(
                        f"WARNING: {self._label(a)} "
                        f"({a.start_time:%H:%M}-{a.end_time:%H:%M}) overlaps "
                        f"{self._label(b)} "
                        f"({b.start_time:%H:%M}-{b.end_time:%H:%M})"
                    )
        return warnings

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
    def _label(entry: ScheduledTask) -> str:
        """Format a slot as 'Pet: Task', or just the task title if no pet is set."""
        if entry.pet_name:
            return f"{entry.pet_name}: '{entry.task.title}'"
        return f"'{entry.task.title}'"

    @staticmethod
    def _to_datetime(t: time) -> datetime:
        """Anchor a time to an arbitrary date so timedelta math works."""
        return datetime(2000, 1, 1, t.hour, t.minute)

    @classmethod
    def _minutes_between(cls, start: time, end: time) -> int:
        """Return the number of whole minutes between two times of day."""
        delta = cls._to_datetime(end) - cls._to_datetime(start)
        return int(delta.total_seconds() // 60)
