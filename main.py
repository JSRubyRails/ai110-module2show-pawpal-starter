from pawpalsystem import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Alex", preferences={"available_time": 180})  # 3 hours

# Create pets
pet1 = Pet(name="Buddy", species="Dog", age=5)
pet2 = Pet(name="Whiskers", species="Cat", age=3)

# Create tasks
task1 = Task(name="Walk Buddy", duration=60, priority=3)
task2 = Task(name="Feed Whiskers", duration=15, priority=2)
task3 = Task(name="Groom Buddy", duration=45, priority=1)
task4 = Task(name="Play with Whiskers", duration=30, priority=2)

# Add tasks to scheduler (for simplicity, all tasks for owner/pet1)
scheduler = Scheduler(owner, pet1, tasks=[task1, task2, task3, task4])
plan = scheduler.generate_plan()

print("Today's Schedule:")
for task in plan:
    print(f"- {task.name} ({task.duration} min, priority {task.priority})")
