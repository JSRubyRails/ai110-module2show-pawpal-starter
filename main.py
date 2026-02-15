from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, timedelta

# Create owner
owner = Owner(name="Alex", preferences={"available_time": 180})  # 3 hours

# Create pet
pet = Pet(name="Buddy", species="Dog", age=5)

# Create tasks OUT OF ORDER with times
task1 = Task(name="Evening walk", duration=30, priority=2, time="18:00")
task2 = Task(name="Morning walk", duration=30, priority=3, time="08:00")
task3 = Task(name="Lunch feeding", duration=15, priority=3, time="12:00")
task4 = Task(name="Afternoon play", duration=45, priority=1, time="15:30")
task5 = Task(name="Grooming session", duration=60, priority=2, time="10:00")
task6 = Task(name="Bedtime routine", duration=20, priority=2, time="21:00")

# Mark some tasks as completed
task2.mark_complete()  # Morning walk is done
task3.mark_complete()  # Lunch feeding is done

# Create scheduler and add tasks
scheduler = Scheduler(owner, pet, tasks=[task1, task2, task3, task4, task5, task6])

print("=" * 60)
print("🐾 PawPal+ Task Management Demo")
print("=" * 60)

# Show original task order
print("\n📋 ORIGINAL TASK ORDER (as added):")
print("-" * 60)
for i, task in enumerate(scheduler.tasks, 1):
    status = "✓" if task.completed else "○"
    print(f"{i}. [{status}] {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")

# Demonstrate sort_by_time()
print("\n⏰ SORTED BY TIME (using sort_by_time()):")
print("-" * 60)
sorted_tasks = scheduler.sort_by_time()
for i, task in enumerate(sorted_tasks, 1):
    status = "✓" if task.completed else "○"
    print(f"{i}. [{status}] {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")

# Demonstrate filter_tasks() - completed tasks only
print("\n✅ COMPLETED TASKS ONLY (using filter_tasks(completed=True)):")
print("-" * 60)
completed_tasks = scheduler.filter_tasks(completed=True)
if completed_tasks:
    for i, task in enumerate(completed_tasks, 1):
        print(f"{i}. {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")
else:
    print("No completed tasks found.")

# Demonstrate filter_tasks() - incomplete tasks only
print("\n○ INCOMPLETE TASKS ONLY (using filter_tasks(completed=False)):")
print("-" * 60)
incomplete_tasks = scheduler.filter_tasks(completed=False)
if incomplete_tasks:
    for i, task in enumerate(incomplete_tasks, 1):
        print(f"{i}. {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")
else:
    print("No incomplete tasks found.")

# Demonstrate filter_tasks() - by pet name
print("\n🐕 TASKS FOR BUDDY (using filter_tasks(pet_name='Buddy')):")
print("-" * 60)
buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
if buddy_tasks:
    for i, task in enumerate(buddy_tasks, 1):
        status = "✓" if task.completed else "○"
        print(f"{i}. [{status}] {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")
else:
    print("No tasks found for Buddy.")

# Combine: incomplete tasks for Buddy, sorted by time
print("\n🎯 INCOMPLETE TASKS FOR BUDDY, SORTED BY TIME:")
print("-" * 60)
incomplete_buddy = scheduler.filter_tasks(completed=False, pet_name="Buddy")
# Sort the filtered results
incomplete_buddy_sorted = sorted(incomplete_buddy, key=lambda t: t.time)
if incomplete_buddy_sorted:
    for i, task in enumerate(incomplete_buddy_sorted, 1):
        print(f"{i}. {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")
else:
    print("No incomplete tasks found for Buddy.")

# Show generated schedule
print("\n📅 GENERATED SCHEDULE (using generate_plan()):")
print("-" * 60)
plan = scheduler.generate_plan()
for i, task in enumerate(plan, 1):
    status = "✓" if task.completed else "○"
    print(f"{i}. [{status}] {task.name:20s} | {task.time} | {task.duration:2d} min | Priority: {task.priority}")

print("\n" + "=" * 60)

# Demonstrate recurring tasks with timedelta
print("\n🔄 RECURRING TASKS DEMO (with timedelta)")
print("=" * 60)

# Create today's date and time
today = datetime.now()
print(f"\n📅 Today: {today.strftime('%Y-%m-%d %H:%M:%S')}")

# Create some recurring tasks with due dates
daily_walk = Task(
    name="Daily morning walk",
    duration=30,
    priority=3,
    time="07:00",
    recurrence="daily",
    due_date=datetime(today.year, today.month, today.day, 7, 0)  # Today at 7:00 AM
)

weekly_vet = Task(
    name="Weekly vet checkup",
    duration=45,
    priority=2,
    time="14:00",
    recurrence="weekly",
    due_date=datetime(today.year, today.month, today.day, 14, 0)  # Today at 2:00 PM
)

# Add to scheduler
scheduler.tasks.append(daily_walk)
scheduler.tasks.append(weekly_vet)

print("\n📋 BEFORE COMPLETING RECURRING TASKS:")
print(f"Total tasks: {len(scheduler.tasks)}")
print(f"- Daily walk: completed={daily_walk.completed}, due={daily_walk.due_date.strftime('%Y-%m-%d %H:%M')}")
print(f"- Weekly vet: completed={weekly_vet.completed}, due={weekly_vet.due_date.strftime('%Y-%m-%d %H:%M')}")

# Mark daily walk as complete (should create new instance with due_date = today + 1 day)
print("\n✅ Marking 'Daily morning walk' as complete...")
print(f"   Original due date: {daily_walk.due_date.strftime('%Y-%m-%d %H:%M')}")
new_daily = scheduler.complete_task(daily_walk)
if new_daily:
    print(f"   → New instance created: '{new_daily.name}' (completed={new_daily.completed})")
    print(f"   → New due date: {new_daily.due_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   → Calculated using: due_date + timedelta(days=1)")

# Mark weekly vet as complete (should create new instance with due_date = today + 7 days)
print("\n✅ Marking 'Weekly vet checkup' as complete...")
print(f"   Original due date: {weekly_vet.due_date.strftime('%Y-%m-%d %H:%M')}")
new_weekly = scheduler.complete_task(weekly_vet)
if new_weekly:
    print(f"   → New instance created: '{new_weekly.name}' (completed={new_weekly.completed})")
    print(f"   → New due date: {new_weekly.due_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   → Calculated using: due_date + timedelta(days=7)")

print("\n📋 AFTER COMPLETING RECURRING TASKS:")
print(f"Total tasks: {len(scheduler.tasks)}")

# Show all tasks with their completion status and due dates
print("\n📊 ALL RECURRING TASKS (showing due dates):")
print("-" * 80)
for task in scheduler.tasks:
    if task.recurrence != "none":
        status = "✓" if task.completed else "○"
        due = task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else "No date"
        print(f"[{status}] {task.name:25s} | Due: {due} | {task.recurrence:7s}")

# Filter to show only incomplete recurring tasks
incomplete_recurring = [t for t in scheduler.tasks if t.recurrence != "none" and not t.completed]
print(f"\n🔄 INCOMPLETE RECURRING TASKS: {len(incomplete_recurring)}")
for task in incomplete_recurring:
    due = task.due_date.strftime('%Y-%m-%d at %H:%M') if task.due_date else "No date set"
    print(f"   - {task.name} ({task.recurrence}) - Due: {due}")

print("\n" + "=" * 60)

# Demonstrate conflict detection
print("\n⚠️  CONFLICT DETECTION DEMO")
print("=" * 60)

# Create some tasks that will conflict
conflict_task1 = Task(
    name="Dog training",
    duration=60,
    priority=3,
    time="10:00",
    due_date=datetime(today.year, today.month, today.day, 10, 0)  # 10:00 AM, 60 min (ends at 11:00)
)

conflict_task2 = Task(
    name="Vet appointment",
    duration=45,
    priority=3,
    time="10:30",
    due_date=datetime(today.year, today.month, today.day, 10, 30)  # 10:30 AM, 45 min (ends at 11:15)
)

conflict_task3 = Task(
    name="Grooming session",
    duration=30,
    priority=2,
    time="12:00",
    due_date=datetime(today.year, today.month, today.day, 12, 0)  # 12:00 PM, 30 min (ends at 12:30)
)

# Add conflicting tasks to scheduler
scheduler.tasks.append(conflict_task1)
scheduler.tasks.append(conflict_task2)
scheduler.tasks.append(conflict_task3)

print("\n📋 SCHEDULED TASKS:")
print("-" * 80)
for task in [conflict_task1, conflict_task2, conflict_task3]:
    start = task.due_date.strftime('%H:%M')
    end = (task.due_date + timedelta(minutes=task.duration)).strftime('%H:%M')
    print(f"- {task.name:20s} | {start} - {end} ({task.duration} min)")

# Detect conflicts
print("\n🔍 DETECTING CONFLICTS...")
conflicts = scheduler.detect_conflicts()

if conflicts:
    print(f"❌ Found {len(conflicts)} conflict(s):\n")
    for task1, task2 in conflicts:
        task1_start = task1.due_date.strftime('%H:%M')
        task1_end = (task1.due_date + timedelta(minutes=task1.duration)).strftime('%H:%M')
        task2_start = task2.due_date.strftime('%H:%M')
        task2_end = (task2.due_date + timedelta(minutes=task2.duration)).strftime('%H:%M')

        print(f"   ⚠️  CONFLICT:")
        print(f"      • {task1.name}: {task1_start} - {task1_end}")
        print(f"      • {task2.name}: {task2_start} - {task2_end}")
        print()
else:
    print("✅ No conflicts detected!")

print("\n" + "=" * 60)
print("✅ All methods tested successfully!")
print("=" * 60)
