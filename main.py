"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the terminal.
Run with: python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


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

    # 3. Add at least three tasks with different durations to the pets.
    mochi.add_task(Task("Morning walk", duration_minutes=30, priority="high", category="walk"))
    mochi.add_task(Task("Breakfast", duration_minutes=10, priority="high", category="feeding"))
    mochi.add_task(Task("Brush coat", duration_minutes=20, priority="low", category="grooming"))

    luna.add_task(Task("Refill food + water", duration_minutes=5, priority="high", category="feeding"))
    luna.add_task(Task("Clean litter box", duration_minutes=15, priority="medium", category="cleaning"))
    luna.add_task(Task("Play / enrichment", duration_minutes=25, priority="medium", category="enrichment"))

    # 4. Build and print today's schedule.
    start = owner.get_preference("day_start")
    budget = owner.get_preference("available_minutes")

    print("=" * 48)
    print("Today's Schedule")
    print("=" * 48)

    for pet in owner.pets:
        scheduler = Scheduler(available_minutes=budget, start_time=start)
        plan = scheduler.build_plan(pet.list_tasks())

        print(f"\n{pet.name} ({pet.breed} {pet.species})")
        print("-" * 48)
        print(plan.explain())


if __name__ == "__main__":
    main()
