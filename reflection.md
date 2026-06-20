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
holds the *algorithm*, and `Plan` holds the *output* — so each can be built and
tested independently.

**b. Design changes**

Yes, two changes emerged once I moved from the diagram to code:

1. **Added a `ScheduledTask` class.** My first sketch had the `Scheduler` place
   tasks directly into the `Plan`, but a `Task` only knows its duration, not *when*
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
  is a *hard* constraint: a task is only placed if `fits()` confirms it still fits in
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
*fail* — you physically cannot fit more than the budget allows, so it determines what
gets dropped. **Priority is the next most important** because it decides *which* tasks
win that limited time: when not everything fits, the high-priority care (meds, feeding)
should be the stuff that survives. Duration is deliberately demoted to a tiebreaker — it
only matters *within* a priority level — so a short low-priority task can never jump
ahead of an important one just because it's small.

**b. Tradeoffs**

The main tradeoff is that the scheduler is **greedy (priority-first), not optimal.** It
sorts by priority and places tasks in that order until the budget runs out — it does
*not* search for the combination of tasks that maximizes how many fit (the knapsack
problem). So it can leave the day "sub-optimal" by raw count: a single high-priority
30-minute task can consume budget that two shorter, slightly-lower-priority tasks would
have filled more completely.

That tradeoff is reasonable for pet care because **importance matters more than count.**
Getting medication and feeding done is worth more than squeezing in the largest possible
number of tasks, and the greedy approach guarantees the most important tasks are never
sacrificed to fit trivial ones. It's also **fast and explainable** — the order is just
"priority, then shortest first," which is exactly what `Plan.explain()` reports back to
the user. A true optimizer would be harder to predict and harder to justify to an owner
who just wants to know *why* a task was skipped. For a daily list of a handful of tasks,
the optimal solution and the greedy one usually coincide anyway, so the extra complexity
wouldn't earn its keep.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
