# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Based on the PawPal+ scenario, the three core actions a user should perform are:

1. Enter owner + pet info — set up who they are and which pet they're planning care for (name, species/breed, etc.).

2. Add/edit care tasks — input the tasks to be scheduled (walks, feeding, meds, grooming, enrichment) with at least a duration and priority for each.

3. Generate the daily plan — run the scheduler to produce a daily schedule based on the constraints (available time, priorities) and view the plan, ideally with an explanation of the reasoning.


Based on these three core actions, I created the following classes:

- **Owner** — the person planning care. Holds `name`, a `preferences` dict, and a
  list of `pets`. Responsible for managing pets and storing planning preferences
  (`add_pet`, `add_preference`, `get_preference`).
- **Pet** — the animal being cared for. Holds `name`, `species`, `breed`, and a list
  of `tasks`. Responsible for managing its own care tasks (`add_task`,
  `remove_task`, `list_tasks`).
- **Task** — a single care action (walk, feeding, meds, grooming, etc.). Holds
  `title`, `duration_minutes`, `priority`, `category`, and `recurrence`. Responsible
  for facts about itself (`is_recurring`, `priority_rank`).
- **Scheduler** — the engine. Holds the constraints (`available_minutes`,
  `start_time`) and owns the algorithm: sort tasks, filter to the time budget, place
  them, and resolve conflicts (`build_plan`, `sort_by_priority`, `fits`,
  `resolve_conflicts`).
- **Plan** — the result a user reads. Holds the scheduled `entries`, `total_minutes`,
  and any `skipped` tasks, and can explain itself and render for display
  (`explain`, `to_table`).

The key responsibility split: `Task` holds data + facts about itself, `Scheduler`
holds the algorithm, and `Plan` holds the output — so each can be built and
tested independently.

**b. Design changes**

Yes, two changes emerged once I moved from the diagram to code:

1. **Added a `ScheduledTask` class.** My first sketch had the `Scheduler` place
   tasks directly into the `Plan`, but a `Task` only knows its duration, not when
   it happens. I introduced `ScheduledTask` to wrap a `Task` with a concrete
   `start_time`/`end_time`, so the `Plan` stores placed slots rather than mutating
   `Task` objects with scheduling-specific fields. This keeps `Task` reusable and
   makes conflict detection (overlapping slots) much cleaner.

2. **Used dataclasses for the data objects.** I made `Task`, `Pet`, `Owner`,
   `ScheduledTask`, and `Plan` Python `@dataclass`es to cut boilerplate, while
   keeping `Scheduler` a plain class because it is behavior, not data. A direct
   consequence: my UML originally listed a `__repr__()` method on `Task`, but
   dataclasses generate that automatically, so I dropped it from the diagram to keep
   it matching the real implementation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers four constraints, which come together in `build_plan`:

- **Time budget** (`available_minutes`) — the total minutes available in the day. This
  is a hard constraint: a task is only placed if `fits()` confirms it still fits in
  the remaining budget, otherwise it goes to the `Plan`'s `skipped` list.
- **Priority** (`high`/`medium`/`low`) — the main ordering signal. `sort_by_priority`
  ranks high-priority tasks first via `priority_rank()`.
- **Duration** (`duration_minutes`) — used as a tiebreaker: among tasks of equal
  priority, shorter ones are placed first so more tasks fit.
- **Start time** (`start_time`) — when the day begins; the placement cursor starts here
  and advances as tasks are laid down. This and `available_minutes` are sourced from the
  Owner's `preferences`, so user preferences feed the constraints rather than being a
  separate one.

I decided **time is the most important** because it's the only constraint that can
fail — you physically cannot fit more than the budget allows, so it determines what
gets dropped. **Priority is the next most important** because it decides which tasks
win that limited time: when not everything fits, the high-priority care (meds, feeding)
should be the stuff that survives. Duration is deliberately demoted to a tiebreaker — it
only matters within a priority level — so a short low-priority task can never jump
ahead of an important one just because it's small.

**b. Tradeoffs**

The main tradeoff is that the scheduler is **greedy (priority-first), not optimal.** It
sorts by priority and places tasks in that order until the budget runs out — it does
not search for the combination of tasks that maximizes how many fit (the knapsack
problem). So it can leave the day "sub-optimal" by raw count: a single high-priority
30-minute task can consume budget that two shorter, slightly-lower-priority tasks would
have filled more completely.

That tradeoff is reasonable for pet care because **importance matters more than count.**
Getting medication and feeding done is worth more than squeezing in the largest possible
number of tasks, and the greedy approach guarantees the most important tasks are never
sacrificed to fit trivial ones. It's also **fast and explainable** — the order is just
"priority, then shortest first," which is exactly what `Plan.explain()` reports back to
the user. A true optimizer would be harder to predict and harder to justify to an owner
who just wants to know why a task was skipped. For a daily list of a handful of tasks,
the optimal solution and the greedy one usually coincide anyway, so the extra complexity
wouldn't earn its keep.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout, but at different "altitudes" depending on the phase:

- **Design brainstorming.** Early on I used it as a sounding board for the class
  breakdown — talking through where scheduling logic should live and whether time
  slots belonged on `Task` or somewhere else. That conversation is what surfaced the
  `ScheduledTask` idea (wrapping a `Task` with concrete start/end times) instead of
  bolting scheduling fields onto `Task`.
- **Implementation.** Once the design was settled, I had AI help fill in the
  mechanical parts — dataclass boilerplate, the `timedelta`-based recurrence math, and
  the pairwise overlap check in `detect_conflicts` — which let me spend my attention on
  the algorithm decisions rather than syntax.
- **Refactoring and consistency.** I used it to keep the artifacts in sync: updating
  the UML diagram to match the real code after I added `status`, `due_date`,
  `detect_conflicts`, `sort_by_time`, etc., and tightening the Streamlit display to
  actually call the `Scheduler` methods (sorting preview, conflict warnings) instead
  of just dumping the plan.

The most helpful prompts were **specific and grounded in my actual code** — e.g.
"does `pawpal_system.py` match this UML diagram?" or "wire the display in `app.py` to
use the Scheduler's conflict warnings." Vague prompts like "build a scheduler" gave
generic answers; pointing at a real file and a concrete behavior gave answers I could
drop in and verify.

**b. Judgment and verification**

One moment I didn't accept a suggestion as-is: the **conflict-handling design**. The
straightforward suggestion was to have the scheduler resolve conflicts automatically
— push overlapping tasks later so the schedule is always "clean." I pushed back on
making that the default, because silently moving a task changes the plan the user
asked for and hides the fact that there was a clash at all. I split it into two
methods instead: `detect_conflicts` is non-destructive and just returns warnings
(so the UI can show them), while `resolve_conflicts` is an explicit, opt-in fix. That
keeps the user informed rather than surprised.

I verified AI suggestions three ways. First, **tests**: the conflict logic is pinned
by `test_detect_conflicts_flags_overlapping_times` and, importantly,
`test_detect_conflicts_allows_back_to_back_slots`, which checks the off-by-one case
where one task ends exactly as the next begins (08:30 end / 08:30 start must not
count as a conflict) — that's the kind of boundary bug an AI's first draft often gets
wrong. Second, **running `main.py`** end to end, which pools two pets onto one timeline
and let me eyeball that sorting, conflict warnings, and filtering all produced sane
output. Third, **reading the code myself** — I treated AI output as a draft to
understand and own, not a black box to paste, which is exactly how I caught the
auto-resolve behavior I didn't want.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 10 tests (`tests/tests_pawpal.py`) covering the behaviors that the rest of
the app depends on:

- **Task completion & pet wiring** — `mark_complete()` flips status to complete, and
  adding a task to a `Pet` grows its task list. These are the basic data invariants
  everything else assumes.
- **Sorting** — `sort_by_time()` returns slots in chronological order (from a
  deliberately shuffled input) without mutating the caller's list, and `build_plan()`
  places tasks high-priority first. Sorting *is* the core algorithm, so it's the thing
  most worth pinning.
- **Recurrence** — completing a `daily` task produces a fresh pending task due exactly
  one day later with its recurrence metadata intact; doing it via `Pet.complete_task()`
  auto-appends that follow-up; and a one-off task spawns nothing. Recurrence is the
  trickiest logic (date math + object creation), so it got the most tests.
- **Conflict detection** — overlapping slots are flagged, and back-to-back slots
  (`a.end == b.start`) are not. That boundary case is the easiest thing to get wrong.
- **Budget handling** — a task that exceeds the remaining time lands in `Plan.skipped`
  rather than being dropped silently, so nothing disappears without explanation.

These were important because they cover the two ways the scheduler could quietly lie
to a user: by **losing a task** (budget/skip handling) or by producing an
order/time that's wrong (sorting and conflict boundaries). Those are exactly the
bugs a casual glance at the UI wouldn't catch.

**b. Confidence**

I'm fairly confident the scheduler works correctly **for the cases it's designed for**:
all 10 tests pass, the boundary conditions (exact-fit budget, touching time slots) are
covered explicitly, and `main.py` exercises the whole pipeline across two pets and
behaves as expected. The logic is also simple and greedy by design, which leaves fewer
places for subtle bugs to hide.

My confidence is lower on inputs the tests don't yet probe. If I had more time I'd add
edge cases for: an **empty task list** and a **zero/negative time budget**; **ties**
where equal priority and equal duration could make ordering ambiguous; a schedule
that **runs past midnight** (since times are `datetime.time`, not full datetimes, slot
math would wrap incorrectly); **`resolve_conflicts` itself** (currently only
`detect_conflicts` is tested); and **weekly recurrence + month/year rollover** (e.g.
completing a task due Jan 31 or Dec 28) to confirm `timedelta` rolls over the way I
claim it does.

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is the **separation of responsibilities** between
`Task` (data + facts about itself), `Scheduler` (the algorithm), and `Plan` (the
output). That split paid off concretely: I could unit-test the algorithm without any
UI, swap the Streamlit display logic without touching the scheduler, and explain each
piece in isolation. The `ScheduledTask` wrapper in particular kept `Task` clean and
reusable and made conflict detection a simple overlap check rather than something
tangled up with task state. It's the design decision that made everything downstream
easier.

**b. What you would improve**

In another iteration I'd move from `datetime.time` to full `datetime` slots so the
schedule can cross midnight and span multiple days, which is the most real limitation
today. I'd also make the multi-pet story first-class: right now each pet is planned on
its own 08:00-start timeline and conflicts only show up once entries are pooled
manually (as `main.py` does) — I'd have the `Scheduler` plan across an owner's pets on
one shared timeline so conflict detection and resolution are part of the normal flow,
not a demo step. Finally, I'd surface `resolve_conflicts` and recurrence in the
Streamlit UI, since both are implemented and tested but the app doesn't expose them yet.

**c. Key takeaway**

The biggest thing I learned is that a clear design is what makes AI collaboration
actually work. When I had a firm responsibility split, I could give the AI small,
well-scoped tasks ("wire the display to the Scheduler's conflict warnings") and verify
each one against a test or a real run. When I was vague, I got generic code I'd have
had to untangle later. The design wasn't just for the humans reading the UML — it was
what let me direct the AI precisely, keep ownership of the decisions (like splitting
detect vs. resolve), and trust the result.
