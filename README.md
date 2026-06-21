# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

The scheduling engine in `pawpal_system.py` implements these algorithms:

- **Priority-first task ordering** — tasks are sorted high → low priority, with shorter tasks breaking ties so more fit in the day (`Scheduler.sort_by_priority`).
- **Greedy time-budget packing** — tasks are placed in priority order only while they fit the remaining minutes; the rest are recorded in `Plan.skipped` rather than dropped silently (`Scheduler.build_plan`, `Scheduler.fits`).
- **Chronological sorting** — placed slots are reordered by start time for display and as a precondition for conflict resolution (`Scheduler.sort_by_time`).
- **Conflict warnings** — every pair of slots is checked for overlap and flagged with a per-pet warning string, non-destructively (`Scheduler.detect_conflicts`).
- **Conflict resolution** — overlapping slots are pushed later in place so no two share a time range (`Scheduler.resolve_conflicts`).
- **Daily & weekly recurrence** — completing a recurring task auto-generates its next occurrence, with `timedelta` handling month/year/leap-year rollover (`Task.next_occurrence`, `Task.mark_complete`, `Pet.complete_task`).
- **Task filtering** — query tasks across all pets by completion status and/or pet name, case-insensitively (`Owner.find_tasks`).
- **Plan explanations** — the generated plan summarizes what was scheduled, in what order, and what was skipped and why (`Plan.explain`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

================================================
Today's Schedule
================================================

Mochi (Shiba Inu dog)
------------------------------------------------
Scheduled 3 task(s) using 60 min, ordered by priority then placed in order:
08:00 — Breakfast (10 min) [priority: high]
08:10 — Morning walk (30 min) [priority: high]
08:40 — Brush coat (20 min) [priority: low]

Luna (Tabby cat)
------------------------------------------------
Scheduled 3 task(s) using 45 min, ordered by priority then placed in order:
08:00 — Refill food + water (5 min) [priority: high]
08:05 — Clean litter box (15 min) [priority: medium]
08:20 — Play / enrichment (25 min) [priority: medium]

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run a single file with verbose output:
python -m pytest tests/tests_pawpal.py -v
```

The tests in `tests/tests_pawpal.py` cover the core scheduling behaviors:

- **Task completion & pet wiring** — `mark_complete()` flips a task's status, and adding a task to a `Pet` updates its task list.
- **Sorting correctness** — `sort_by_time()` returns scheduled slots in chronological (start-time) order, and `build_plan()` places tasks high-priority first.
- **Recurrence logic** — completing a `daily` task creates a new pending task due the following day; completing it via `Pet.complete_task()` auto-appends that follow-up, while a one-off task spawns nothing.
- **Conflict detection** — `detect_conflicts()` flags overlapping/duplicate time slots and correctly leaves back-to-back slots (where one ends exactly as the next begins) unflagged.
- **Budget handling** — tasks that exceed the remaining time budget are recorded in `Plan.skipped` rather than dropped silently.

Sample test output:

```
================================================================================== test session starts ==================================================================================
platform darwin -- Python 3.11.9, pytest-8.4.1, pluggy-1.6.0 -- /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
cachedir: .pytest_cache
rootdir: /Users/elias/ai110-module2show-pawpal-starter
plugins: anyio-4.10.0
collected 10 items                                                                                                                                                                      

tests/tests_pawpal.py::test_task_completion_changes_status PASSED                                                                                                                 [ 10%]
tests/tests_pawpal.py::test_adding_task_increases_pet_task_count PASSED                                                                                                           [ 20%]
tests/tests_pawpal.py::test_sort_by_time_returns_chronological_order PASSED                                                                                                       [ 30%]
tests/tests_pawpal.py::test_completing_daily_task_creates_task_for_following_day PASSED                                                                                           [ 40%]
tests/tests_pawpal.py::test_completing_recurring_task_via_pet_appends_followup PASSED                                                                                             [ 50%]
tests/tests_pawpal.py::test_completing_non_recurring_task_creates_no_followup PASSED                                                                                              [ 60%]
tests/tests_pawpal.py::test_detect_conflicts_flags_overlapping_times PASSED                                                                                                       [ 70%]
tests/tests_pawpal.py::test_detect_conflicts_allows_back_to_back_slots PASSED                                                                                                     [ 80%]
tests/tests_pawpal.py::test_build_plan_skips_tasks_that_exceed_budget PASSED                                                                                                      [ 90%]
tests/tests_pawpal.py::test_build_plan_orders_by_priority_high_first PASSED                                                                                                       [100%]

==============================================================================
10 passed in 0.01s ===============================================================================

```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Priority-first (high → low) with shorter duration as a tiebreaker; separately, sort placed slots chronologically by start time |
| Filtering | `Owner.find_tasks()`, `Scheduler.fits()` + `Plan.skipped` | Query tasks by completion status and/or pet name; tasks that don't fit the time budget are skipped, not dropped silently |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.resolve_conflicts()` | Detection returns warning strings (non-destructive); resolution pushes overlapping slots later |
| Recurring tasks | `Task.next_occurrence()`, `Task.mark_complete()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next occurrence using `timedelta` |

### Sorting behavior

Two distinct sorts, because "what order to *place* tasks in" and "what order to *display*
them in" are different questions:

- **`sort_by_priority(tasks)`** orders by a key of `(-priority_rank(), duration_minutes)`,
  so high-priority tasks come first and, among equal priorities, shorter tasks come first
  to pack more in. This is what `build_plan` uses to decide placement order.
- **`sort_by_time(scheduled)`** orders placed `ScheduledTask` slots chronologically by
  `start_time`. Because `start_time` is a `datetime.time`, the sort key is the time object
  itself — no string parsing. This is mainly useful once slots from multiple pets are
  pooled into one timeline (and as a precondition for `resolve_conflicts`).

### Filtering behavior

- **`Owner.find_tasks(completed=None, pet_name=None)`** searches every task across all the
  owner's pets, filtering by completion status and/or pet name (case-insensitive). Both
  filters are optional keyword args, so the same method covers "all pending tasks", "all of
  Mochi's tasks", "Mochi's completed tasks", or "everything".
- **Time-budget filtering** happens during planning: `build_plan` only places a task if
  `fits()` confirms it's within the remaining minutes; anything that doesn't fit is recorded
  in `Plan.skipped` so the user can see *what* was left out and why.

### Conflict detection logic

Detection is intentionally **lightweight and non-destructive** — it returns a warning rather
than raising or rewriting the schedule:

- **`detect_conflicts(scheduled)`** compares every pair of slots and flags any whose time
  ranges overlap (`a.start < b.end and b.start < a.end`). It returns a list of warning
  strings (empty if there are none) and labels each side with its pet, so cross-pet clashes
  read like `Mochi: 'Breakfast' (08:00-08:10) overlaps Luna: 'Refill food + water' (08:00-08:05)`.
- **`resolve_conflicts(scheduled)`** is the optional "fix it" counterpart: it pushes
  overlapping slots later in place so no two share a time range (assumes start-time order,
  which `sort_by_time` guarantees).

### Recurring task logic

Recurrence is driven by a small `RECURRENCE_DELTAS` map and `datetime.timedelta`:

- **`Task.next_occurrence()`** builds a fresh `pending` copy of a recurring task with its
  `due_date` advanced by the recurrence interval (`timedelta(days=1)` for daily,
  `timedelta(weeks=1)` for weekly). Using `date + timedelta` means month/year/leap-year
  rollovers are handled automatically. Non-recurring tasks return `None`.
- **`Task.mark_complete()`** marks the task done and returns that next occurrence (or `None`).
- **`Pet.complete_task(index)`** ties it together: it completes the task and, if a follow-up
  was created, appends it to the pet's list — so finishing today's walk automatically queues
  tomorrow's.

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) is organized top to bottom around one care plan:

- **Owner & Pet** — enter an owner name, a pet name, and pick a species. The pet object persists across reruns and is rebuilt automatically when you change the name.
- **Tasks** — add tasks with a title, duration (minutes), and priority (low/medium/high). Existing tasks are shown in a live table **sorted by priority**, previewing the order the scheduler will use.
- **Build Schedule** — set the time available for the day (minutes) and generate a plan with one click.
- **Results** — the generated plan is shown as a table, a success banner reports how many tasks fit and the minutes used, conflict warnings appear for any overlapping slots, a plain-text explanation describes the reasoning, and any tasks that didn't fit are listed as skipped.

### Example workflow

1. **Add a pet** — type an owner name (e.g. *Jordan*) and a pet name (e.g. *Mochi*), and choose a species.
2. **Add tasks** — add "Morning walk" (30 min, high), "Breakfast" (10 min, high), and "Brush coat" (20 min, low). The task table immediately re-sorts so the high-priority tasks rise to the top.
3. **Set the time budget** — enter the minutes available today (e.g. 120).
4. **Generate the schedule** — click **Generate schedule** to build the plan.
5. **View today's schedule** — read the timed table, the success banner, the "Why this plan?" explanation, and any conflict or skipped-task warnings.

### Key Scheduler behaviors shown

- **Priority sorting** — `sort_by_priority` places high-priority tasks first, using shorter duration as a tiebreaker (Breakfast before Morning walk, Brush coat last).
- **Greedy time-budget packing** — `build_plan` only schedules tasks that fit the remaining minutes; the rest land in `Plan.skipped`.
- **Chronological sorting** — `sort_by_time` reorders pooled slots by start time (useful when multiple pets share one timeline).
- **Conflict warnings** — `detect_conflicts` flags overlapping slots non-destructively, labeling each side with its pet.
- **Plan explanation** — `Plan.explain` summarizes what was scheduled, in what order, and what was skipped.

### Sample CLI output

The command-line demo (`python main.py`) exercises the same engine across two pets and prints sorting, conflict detection, and filtering:

```
====================================================
Today's Schedule
====================================================

Mochi (Shiba Inu dog)
----------------------------------------------------
Scheduled 3 task(s) using 60 min, ordered by priority then placed in order:
08:00 — Breakfast (10 min) [priority: high]
08:10 — Morning walk (30 min) [priority: high]
08:40 — Brush coat (20 min) [priority: low]

Luna (Tabby cat)
----------------------------------------------------
Scheduled 3 task(s) using 45 min, ordered by priority then placed in order:
08:00 — Refill food + water (5 min) [priority: high]
08:05 — Clean litter box (15 min) [priority: medium]
08:20 — Play / enrichment (25 min) [priority: medium]

====================================================
Combined entries BEFORE sort_by_time (pooled per pet)
====================================================
  08:00-08:10  Breakfast
  08:10-08:40  Morning walk
  08:40-09:00  Brush coat
  08:00-08:05  Refill food + water
  08:05-08:20  Clean litter box
  08:20-08:45  Play / enrichment

====================================================
Combined entries AFTER sort_by_time (chronological)
====================================================
  08:00-08:10  Breakfast
  08:00-08:05  Refill food + water
  08:05-08:20  Clean litter box
  08:10-08:40  Morning walk
  08:20-08:45  Play / enrichment
  08:40-09:00  Brush coat

====================================================
Conflict detection across the combined timeline
====================================================
Found 5 conflict(s):
  WARNING: Mochi: 'Breakfast' (08:00-08:10) overlaps Luna: 'Refill food + water' (08:00-08:05)
  WARNING: Mochi: 'Breakfast' (08:00-08:10) overlaps Luna: 'Clean litter box' (08:05-08:20)
  WARNING: Mochi: 'Morning walk' (08:10-08:40) overlaps Luna: 'Clean litter box' (08:05-08:20)
  WARNING: Mochi: 'Morning walk' (08:10-08:40) overlaps Luna: 'Play / enrichment' (08:20-08:45)
  WARNING: Mochi: 'Brush coat' (08:40-09:00) overlaps Luna: 'Play / enrichment' (08:20-08:45)

====================================================
Filtering with Owner.find_tasks
====================================================

Pending tasks (4):
  - Brush coat [pending]
  - Morning walk [pending]
  - Play / enrichment [pending]
  - Clean litter box [pending]

Completed tasks (2):
  - Breakfast [complete]
  - Refill food + water [complete]

All of Mochi's tasks (3):
  - Brush coat [pending]
  - Morning walk [pending]
  - Breakfast [complete]
```
