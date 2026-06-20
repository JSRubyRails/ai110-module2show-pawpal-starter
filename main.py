"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the terminal,
then demonstrates the Scheduler.sort_by_time and Owner.find_tasks methods.
Run with: python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, ScheduledTask, Task


def main() -> None:
    # 1. Create an owner.
    owner = Owner(name="Jordan")
    owner.add_preference("day_start", time(8, 0))
    owner.add_preference("available_minutes", 120)

    # 2. Create at least two pets.
    mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu")
    luna = Pet(name="Luna", species="cat", breed="Tabby")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 3. Add tasks deliberately OUT OF ORDER (mixed priorities/durations) so the
    #    sorting methods have something real to do.
    mochi.add_task(Task("Brush coat", duration_minutes=20, priority="low", category="grooming"))
    mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high", category="walk"))
    mochi.add_task(Task("Breakfast", duration_minutes=10, priority="high", category="feeding"))

    luna.add_task(Task("Play / enrichment", duration_minutes=25, priority="medium", category="enrichment"))
    luna.add_task(Task("Refill food + water", duration_minutes=5, priority="high", category="feeding"))
    luna.add_task(Task("Clean litter box", duration_minutes=15, priority="medium", category="cleaning"))

    # Mark a couple of tasks complete so the status filter has something to show.
    mochi.tasks[2].mark_complete()   # Breakfast
    luna.tasks[1].mark_complete()    # Refill food + water

    start = owner.get_preference("day_start")
    budget = owner.get_preference("available_minutes")

    # 4. Build and print today's schedule per pet.
    print("=" * 52)
    print("Today's Schedule")
    print("=" * 52)

    all_entries: list[ScheduledTask] = []
    for pet in owner.pets:
        scheduler = Scheduler(available_minutes=budget, start_time=start)
        plan = scheduler.build_plan(pet.list_tasks(), pet_name=pet.name)
        all_entries.extend(plan.entries)

        print(f"\n{pet.name} ({pet.breed} {pet.species})")
        print("-" * 52)
        print(plan.explain())

    # 5. Demonstrate sort_by_time: pool every pet's entries together (now
    #    interleaved and out of order) and sort the combined list by start time.
    scheduler = Scheduler(available_minutes=budget, start_time=start)

    print("\n" + "=" * 52)
    print("Combined entries BEFORE sort_by_time (pooled per pet)")
    print("=" * 52)
    for e in all_entries:
        print(f"  {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.task.title}")

    print("\n" + "=" * 52)
    print("Combined entries AFTER sort_by_time (chronological)")
    print("=" * 52)
    for e in scheduler.sort_by_time(all_entries):
        print(f"  {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.task.title}")

    # 5b. Detect conflicts. Each pet's plan starts at 08:00, so once pooled the
    #     two pets have tasks at the same time -> the Scheduler should warn
    #     (rather than crash) about the overlapping slots.
    print("\n" + "=" * 52)
    print("Conflict detection across the combined timeline")
    print("=" * 52)
    conflicts = scheduler.detect_conflicts(all_entries)
    if conflicts:
        print(f"Found {len(conflicts)} conflict(s):")
        for w in conflicts:
            print(f"  {w}")
    else:
        print("No scheduling conflicts found.")

    # 6. Demonstrate find_tasks filtering by status and by pet name.
    print("\n" + "=" * 52)
    print("Filtering with Owner.find_tasks")
    print("=" * 52)

    pending = owner.find_tasks(completed=False)
    print(f"\nPending tasks ({len(pending)}):")
    for t in pending:
        print(f"  - {t.title} [{t.status}]")

    done = owner.find_tasks(completed=True)
    print(f"\nCompleted tasks ({len(done)}):")
    for t in done:
        print(f"  - {t.title} [{t.status}]")

    mochi_tasks = owner.find_tasks(pet_name="Mochi")
    print(f"\nAll of Mochi's tasks ({len(mochi_tasks)}):")
    for t in mochi_tasks:
        print(f"  - {t.title} [{t.status}]")


if __name__ == "__main__":
    main()
