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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
