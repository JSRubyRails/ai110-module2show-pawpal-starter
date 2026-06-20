"""Tests for PawPal+ core behaviors."""

import os
import sys
from datetime import date, time

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, ScheduledTask, Scheduler, Task


def test_task_completion_changes_status():
    """Calling mark_complete() should change the task's status to complete."""
    task = Task("Morning walk", duration_minutes=30)

    # Starts out not complete.
    assert task.status == "pending"
    assert task.is_complete() is False

    task.mark_complete()

    # Status actually changed.
    assert task.status == "complete"
    assert task.is_complete() is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Mochi", species="dog")

    assert len(pet.list_tasks()) == 0

    pet.add_task(Task("Breakfast", duration_minutes=10))

    assert len(pet.list_tasks()) == 1


# --- Sorting correctness -------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return scheduled tasks in start-time order."""
    scheduler = Scheduler(available_minutes=240)
    late = ScheduledTask(Task("Dinner", 20), start_time=time(18, 0), end_time=time(18, 20))
    early = ScheduledTask(Task("Walk", 30), start_time=time(8, 0), end_time=time(8, 30))
    midday = ScheduledTask(Task("Lunch", 15), start_time=time(12, 0), end_time=time(12, 15))

    # Deliberately out of order.
    ordered = scheduler.sort_by_time([late, midday, early])

    start_times = [entry.start_time for entry in ordered]
    assert start_times == [time(8, 0), time(12, 0), time(18, 0)]
    # Sort must not mutate the input list.
    assert start_times == sorted(start_times)


# --- Recurrence logic ----------------------------------------------------


def test_completing_daily_task_creates_task_for_following_day():
    """Marking a daily task complete should create a fresh task due the next day."""
    task = Task("Morning walk", duration_minutes=30, recurrence="daily", due_date=date(2026, 6, 20))

    follow_up = task.mark_complete()

    # Original is now complete; a follow-up was generated.
    assert task.is_complete() is True
    assert follow_up is not None
    # The new task is pending and due exactly one day later.
    assert follow_up.status == "pending"
    assert follow_up.due_date == date(2026, 6, 21)
    # Recurrence metadata carries over so it keeps repeating.
    assert follow_up.recurrence == "daily"
    assert follow_up.title == task.title


def test_completing_recurring_task_via_pet_appends_followup():
    """Pet.complete_task should auto-append the next occurrence to the pet."""
    pet = Pet("Mochi", species="dog")
    pet.add_task(Task("Feed", duration_minutes=10, recurrence="daily", due_date=date(2026, 6, 20)))

    follow_up = pet.complete_task(0)

    assert follow_up is not None
    assert len(pet.list_tasks()) == 2
    assert pet.list_tasks()[1].due_date == date(2026, 6, 21)


def test_completing_non_recurring_task_creates_no_followup():
    """A one-off task should not spawn a follow-up when completed."""
    pet = Pet("Mochi", species="dog")
    pet.add_task(Task("Vet visit", duration_minutes=45))  # recurrence defaults to "none"

    follow_up = pet.complete_task(0)

    assert follow_up is None
    assert len(pet.list_tasks()) == 1


# --- Conflict detection --------------------------------------------------


def test_detect_conflicts_flags_overlapping_times():
    """Two slots sharing a time range should be flagged as a conflict."""
    scheduler = Scheduler(available_minutes=240)
    # Same start time -> duplicate/overlapping slot.
    a = ScheduledTask(Task("Walk", 30), start_time=time(8, 0), end_time=time(8, 30), pet_name="Mochi")
    b = ScheduledTask(Task("Feed", 15), start_time=time(8, 0), end_time=time(8, 15), pet_name="Mochi")

    warnings = scheduler.detect_conflicts([a, b])

    assert len(warnings) == 1
    assert "overlaps" in warnings[0]


def test_detect_conflicts_allows_back_to_back_slots():
    """Slots that touch at the boundary (a.end == b.start) must not conflict."""
    scheduler = Scheduler(available_minutes=240)
    a = ScheduledTask(Task("Walk", 30), start_time=time(8, 0), end_time=time(8, 30))
    b = ScheduledTask(Task("Feed", 15), start_time=time(8, 30), end_time=time(8, 45))

    assert scheduler.detect_conflicts([a, b]) == []


# --- Scheduling / budget edge cases --------------------------------------


def test_build_plan_skips_tasks_that_exceed_budget():
    """Tasks that don't fit the time budget should land in plan.skipped."""
    scheduler = Scheduler(available_minutes=30, start_time=time(8, 0))
    fits = Task("Quick walk", duration_minutes=30, priority="high")
    too_long = Task("Long groom", duration_minutes=60, priority="high")

    plan = scheduler.build_plan([fits, too_long])

    assert [e.task.title for e in plan.entries] == ["Quick walk"]
    assert plan.skipped == [too_long]
    assert plan.total_minutes == 30


def test_build_plan_orders_by_priority_high_first():
    """High-priority tasks should be scheduled before lower-priority ones."""
    scheduler = Scheduler(available_minutes=240, start_time=time(8, 0))
    low = Task("Brush", duration_minutes=10, priority="low")
    high = Task("Meds", duration_minutes=10, priority="high")
    medium = Task("Play", duration_minutes=10, priority="medium")

    plan = scheduler.build_plan([low, high, medium])

    assert [e.task.title for e in plan.entries] == ["Meds", "Play", "Brush"]
