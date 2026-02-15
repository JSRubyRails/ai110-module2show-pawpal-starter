import pytest
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime, timedelta

def test_task_completion():
    task = Task(name="Feed", duration=10, priority=1)
    assert not task.completed
    task.mark_complete()
    assert task.completed

def test_task_addition():
    pet = Pet(name="Buddy", species="Dog", age=5)
    initial_count = len(pet.tasks)
    task = Task(name="Walk", duration=30, priority=2)
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] == task


# ============================================================================
# SORTING CORRECTNESS TESTS
# ============================================================================

def test_sort_by_time_happy_path():
    """Happy Path: Tasks with different times are returned in chronological order"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    # Create tasks OUT OF ORDER
    task1 = Task(name="Evening walk", duration=30, priority=2, time="18:00")
    task2 = Task(name="Morning walk", duration=30, priority=3, time="08:00")
    task3 = Task(name="Lunch feeding", duration=15, priority=3, time="12:00")
    task4 = Task(name="Afternoon play", duration=45, priority=1, time="15:30")

    scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3, task4])
    sorted_tasks = scheduler.sort_by_time()

    # Verify chronological order
    assert len(sorted_tasks) == 4
    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[1].time == "12:00"
    assert sorted_tasks[2].time == "15:30"
    assert sorted_tasks[3].time == "18:00"
    assert sorted_tasks[0].name == "Morning walk"
    assert sorted_tasks[1].name == "Lunch feeding"


def test_sort_by_time_empty_list():
    """Edge Case: Empty task list returns empty list"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)
    scheduler = Scheduler(owner, pet, tasks=[])

    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks == []


def test_sort_by_time_single_task():
    """Edge Case: Single task returns list with that task"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)
    task = Task(name="Walk", duration=30, priority=2, time="10:00")
    scheduler = Scheduler(owner, pet, tasks=[task])

    sorted_tasks = scheduler.sort_by_time()
    assert len(sorted_tasks) == 1
    assert sorted_tasks[0] == task


def test_sort_by_time_all_none():
    """Edge Case: All tasks with time=None returns tasks in original order"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task1 = Task(name="Task A", duration=30, priority=2, time=None)
    task2 = Task(name="Task B", duration=20, priority=3, time=None)
    task3 = Task(name="Task C", duration=15, priority=1, time=None)

    scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3])
    sorted_tasks = scheduler.sort_by_time()

    # Tasks without time should be at the end in original order
    assert len(sorted_tasks) == 3
    assert sorted_tasks[0].name == "Task A"
    assert sorted_tasks[1].name == "Task B"
    assert sorted_tasks[2].name == "Task C"


def test_sort_by_time_mixed_none_and_valid():
    """Edge Case: Mix of None and valid times - None tasks appear at end"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task1 = Task(name="No time A", duration=30, priority=2, time=None)
    task2 = Task(name="Morning", duration=20, priority=3, time="08:00")
    task3 = Task(name="No time B", duration=15, priority=1, time=None)
    task4 = Task(name="Evening", duration=25, priority=2, time="18:00")

    scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3, task4])
    sorted_tasks = scheduler.sort_by_time()

    # First two should be timed tasks in chronological order
    assert sorted_tasks[0].name == "Morning"
    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[1].name == "Evening"
    assert sorted_tasks[1].time == "18:00"

    # Last two should be tasks without time
    assert sorted_tasks[2].time is None
    assert sorted_tasks[3].time is None


def test_sort_by_time_duplicate_times():
    """Edge Case: Multiple tasks at same time - order preserved"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task1 = Task(name="Task A", duration=30, priority=2, time="10:00")
    task2 = Task(name="Task B", duration=20, priority=3, time="10:00")
    task3 = Task(name="Task C", duration=15, priority=1, time="10:00")

    scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3])
    sorted_tasks = scheduler.sort_by_time()

    # All should have same time
    assert len(sorted_tasks) == 3
    assert all(task.time == "10:00" for task in sorted_tasks)
    # Original order should be preserved (stable sort)
    assert sorted_tasks[0].name == "Task A"
    assert sorted_tasks[1].name == "Task B"
    assert sorted_tasks[2].name == "Task C"


# ============================================================================
# RECURRENCE LOGIC TESTS
# ============================================================================

def test_daily_recurrence_happy_path():
    """Happy Path: Marking daily task complete creates new task for next day"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    # Create daily recurring task with due date
    today = datetime(2024, 2, 14, 8, 0)  # Feb 14, 2024 at 8:00 AM
    daily_task = Task(
        name="Daily walk",
        duration=30,
        priority=3,
        time="08:00",
        recurrence="daily",
        due_date=today
    )

    scheduler = Scheduler(owner, pet, tasks=[daily_task])
    initial_count = len(scheduler.tasks)

    # Mark task complete
    new_task = scheduler.complete_task(daily_task)

    # Verify original task is marked complete
    assert daily_task.completed is True

    # Verify new task was created
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.name == "Daily walk"
    assert new_task.recurrence == "daily"

    # Verify new task due date is next day
    expected_due = today + timedelta(days=1)
    assert new_task.due_date == expected_due

    # Verify task was added to scheduler
    assert len(scheduler.tasks) == initial_count + 1
    assert new_task in scheduler.tasks


def test_weekly_recurrence_happy_path():
    """Happy Path: Marking weekly task complete creates new task for next week"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    # Create weekly recurring task
    today = datetime(2024, 2, 14, 14, 0)  # Feb 14, 2024 at 2:00 PM
    weekly_task = Task(
        name="Weekly vet checkup",
        duration=45,
        priority=2,
        time="14:00",
        recurrence="weekly",
        due_date=today
    )

    scheduler = Scheduler(owner, pet, tasks=[weekly_task])

    # Mark task complete
    new_task = scheduler.complete_task(weekly_task)

    # Verify new task due date is 7 days later
    expected_due = today + timedelta(days=7)
    assert new_task.due_date == expected_due
    assert new_task.recurrence == "weekly"


def test_non_recurring_task_no_new_instance():
    """Happy Path: Non-recurring task returns None when completed"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task = Task(name="One-time grooming", duration=60, priority=2, recurrence="none")
    scheduler = Scheduler(owner, pet, tasks=[task])
    initial_count = len(scheduler.tasks)

    # Mark task complete
    new_task = scheduler.complete_task(task)

    # Verify no new task created
    assert new_task is None
    assert task.completed is True
    assert len(scheduler.tasks) == initial_count  # No new task added


def test_daily_recurrence_no_due_date():
    """Edge Case: Daily task without due_date uses current time + 1 day"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    # Task without due_date
    task = Task(
        name="Daily feeding",
        duration=15,
        priority=3,
        time="09:00",
        recurrence="daily",
        due_date=None
    )

    scheduler = Scheduler(owner, pet, tasks=[task])

    # Capture time before marking complete
    before_complete = datetime.now()
    new_task = scheduler.complete_task(task)
    after_complete = datetime.now()

    # New task should have due_date approximately 1 day from now
    assert new_task is not None
    assert new_task.due_date is not None

    # Due date should be roughly 1 day from now (allowing small time difference)
    expected_min = before_complete + timedelta(days=1)
    expected_max = after_complete + timedelta(days=1)
    assert expected_min <= new_task.due_date <= expected_max


def test_daily_recurrence_month_boundary():
    """Edge Case: Daily task on Jan 31 creates task on Feb 1"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    jan_31 = datetime(2024, 1, 31, 10, 0)
    task = Task(
        name="Daily walk",
        duration=30,
        priority=3,
        recurrence="daily",
        due_date=jan_31
    )

    scheduler = Scheduler(owner, pet, tasks=[task])
    new_task = scheduler.complete_task(task)

    # Should be Feb 1
    assert new_task.due_date == datetime(2024, 2, 1, 10, 0)


def test_daily_recurrence_year_boundary():
    """Edge Case: Daily task on Dec 31 creates task on Jan 1 next year"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    dec_31 = datetime(2024, 12, 31, 10, 0)
    task = Task(
        name="Daily walk",
        duration=30,
        priority=3,
        recurrence="daily",
        due_date=dec_31
    )

    scheduler = Scheduler(owner, pet, tasks=[task])
    new_task = scheduler.complete_task(task)

    # Should be Jan 1, 2025
    assert new_task.due_date == datetime(2025, 1, 1, 10, 0)


def test_complete_recurring_task_twice():
    """Edge Case: Completing same recurring task twice creates two new instances"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14, 8, 0)
    task1 = Task(
        name="Daily walk",
        duration=30,
        priority=3,
        recurrence="daily",
        due_date=today
    )

    scheduler = Scheduler(owner, pet, tasks=[task1])

    # Complete first time
    task2 = scheduler.complete_task(task1)
    assert task2.due_date == today + timedelta(days=1)

    # Complete second time
    task3 = scheduler.complete_task(task2)
    assert task3.due_date == today + timedelta(days=2)

    # Should have 3 tasks total (original + 2 new)
    assert len(scheduler.tasks) == 3


def test_recurring_task_added_to_pet():
    """Edge Case: New recurring task is added to pet's task list"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14, 8, 0)
    task = Task(
        name="Daily walk",
        duration=30,
        priority=3,
        recurrence="daily",
        due_date=today
    )

    scheduler = Scheduler(owner, pet, tasks=[task])
    initial_pet_tasks = len(pet.tasks)

    new_task = scheduler.complete_task(task)

    # Verify task was added to pet's task list
    assert len(pet.tasks) == initial_pet_tasks + 1
    assert new_task in pet.tasks


# ============================================================================
# CONFLICT DETECTION TESTS
# ============================================================================

def test_conflict_detection_overlapping_tasks():
    """Happy Path: Two overlapping tasks are flagged as conflict"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 10:00-11:00
    task_a = Task(
        name="Training",
        duration=60,
        priority=3,
        time="10:00",
        due_date=datetime(today.year, today.month, today.day, 10, 0)
    )

    # Task B: 10:30-11:15 (overlaps with Task A)
    task_b = Task(
        name="Vet appointment",
        duration=45,
        priority=3,
        time="10:30",
        due_date=datetime(today.year, today.month, today.day, 10, 30)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b])
    conflicts = scheduler.detect_conflicts()

    # Should detect 1 conflict
    assert len(conflicts) == 1
    assert (task_a, task_b) in conflicts or (task_b, task_a) in conflicts


def test_conflict_detection_duplicate_start_times():
    """Happy Path: Tasks at exact same time are flagged as conflict"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14, 10, 0)

    # Both tasks start at 10:00
    task1 = Task(
        name="Walk",
        duration=30,
        priority=3,
        due_date=today
    )
    task2 = Task(
        name="Feeding",
        duration=20,
        priority=3,
        due_date=today
    )

    scheduler = Scheduler(owner, pet, tasks=[task1, task2])
    conflicts = scheduler.detect_conflicts()

    # Should detect conflict
    assert len(conflicts) == 1


def test_conflict_detection_no_conflicts():
    """Happy Path: Non-overlapping tasks have no conflicts"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 09:00-10:00
    task_a = Task(
        name="Morning walk",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 9, 0)
    )

    # Task B: 11:00-12:00 (no overlap)
    task_b = Task(
        name="Lunch feeding",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 11, 0)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b])
    conflicts = scheduler.detect_conflicts()

    # No conflicts
    assert len(conflicts) == 0


def test_conflict_detection_empty_list():
    """Edge Case: Empty task list returns no conflicts"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)
    scheduler = Scheduler(owner, pet, tasks=[])

    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


def test_conflict_detection_single_task():
    """Edge Case: Single task has no conflicts"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task = Task(
        name="Walk",
        duration=30,
        priority=3,
        due_date=datetime(2024, 2, 14, 10, 0)
    )
    scheduler = Scheduler(owner, pet, tasks=[task])

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


def test_conflict_detection_boundary_touching():
    """Edge Case: Tasks that end/start at same time (boundary touching)"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 10:00-11:00 (ends at 11:00)
    task_a = Task(
        name="Morning walk",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 10, 0)
    )

    # Task B: 11:00-12:00 (starts at 11:00)
    task_b = Task(
        name="Lunch feeding",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 11, 0)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b])
    conflicts = scheduler.detect_conflicts()

    # Current implementation: boundary touching is NOT a conflict
    # (uses < and > not <= and >=)
    assert len(conflicts) == 0


def test_conflict_detection_no_due_dates():
    """Edge Case: Tasks without due_date do not cause conflicts"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    task1 = Task(name="Task A", duration=30, priority=3, due_date=None)
    task2 = Task(name="Task B", duration=30, priority=3, due_date=None)

    scheduler = Scheduler(owner, pet, tasks=[task1, task2])
    conflicts = scheduler.detect_conflicts()

    # No due_date means no conflict detection
    assert len(conflicts) == 0


def test_conflict_detection_mixed_dated_and_none():
    """Edge Case: Mix of tasks with/without due_date - only compares dated tasks"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14, 10, 0)

    task1 = Task(name="Dated A", duration=60, priority=3, due_date=today)
    task2 = Task(name="Dated B", duration=60, priority=3, due_date=today)
    task3 = Task(name="No date A", duration=30, priority=3, due_date=None)
    task4 = Task(name="No date B", duration=30, priority=3, due_date=None)

    scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3, task4])
    conflicts = scheduler.detect_conflicts()

    # Only dated tasks conflict (task1 and task2)
    assert len(conflicts) == 1


def test_conflict_detection_different_days():
    """Edge Case: Same time on different days should not conflict"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    # Task A: Feb 14 at 10:00
    task_a = Task(
        name="Walk today",
        duration=60,
        priority=3,
        due_date=datetime(2024, 2, 14, 10, 0)
    )

    # Task B: Feb 15 at 10:00 (next day)
    task_b = Task(
        name="Walk tomorrow",
        duration=60,
        priority=3,
        due_date=datetime(2024, 2, 15, 10, 0)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b])
    conflicts = scheduler.detect_conflicts()

    # Different days = no conflict
    assert len(conflicts) == 0


def test_conflict_detection_complete_overlap():
    """Edge Case: One task completely contains another"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 09:00-12:00 (3 hours)
    task_a = Task(
        name="Long activity",
        duration=180,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 9, 0)
    )

    # Task B: 10:00-11:00 (inside Task A)
    task_b = Task(
        name="Short activity",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 10, 0)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b])
    conflicts = scheduler.detect_conflicts()

    # Should detect conflict
    assert len(conflicts) == 1


def test_conflict_detection_multiple_conflicts():
    """Edge Case: Multiple overlapping conflicts (chain)"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 10:00-12:00
    task_a = Task(
        name="Task A",
        duration=120,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 10, 0)
    )

    # Task B: 11:00-13:00 (overlaps A)
    task_b = Task(
        name="Task B",
        duration=120,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 11, 0)
    )

    # Task C: 12:00-14:00 (overlaps B)
    task_c = Task(
        name="Task C",
        duration=120,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 12, 0)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b, task_c])
    conflicts = scheduler.detect_conflicts()

    # Should detect: A-B conflict, B-C conflict (possibly A-C if they overlap)
    assert len(conflicts) >= 2


def test_conflict_detection_one_task_conflicts_with_multiple():
    """Edge Case: One long task conflicts with multiple shorter tasks"""
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=5)

    today = datetime(2024, 2, 14)

    # Task A: 10:00-14:00 (4 hours)
    task_a = Task(
        name="Long task",
        duration=240,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 10, 0)
    )

    # Task B: 11:00-12:00
    task_b = Task(
        name="Task B",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 11, 0)
    )

    # Task C: 12:30-13:30
    task_c = Task(
        name="Task C",
        duration=60,
        priority=3,
        due_date=datetime(today.year, today.month, today.day, 12, 30)
    )

    scheduler = Scheduler(owner, pet, tasks=[task_a, task_b, task_c])
    conflicts = scheduler.detect_conflicts()

    # Task A conflicts with both B and C
    assert len(conflicts) == 2
