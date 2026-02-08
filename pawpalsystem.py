from dataclasses import dataclass

class Owner:
    def __init__(self, name, preferences=None):
        self.name = name
        self.preferences = preferences or {}

    def update_preferences(self, new_preferences):
        """Update the owner's preferences with the provided key-value pairs."""
        self.preferences.update(new_preferences)

    def get_info(self):
        """Return a dictionary containing the owner's name and preferences."""
        return {'name': self.name, 'preferences': self.preferences}

@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list = None

    def __post_init__(self):
        """Initialize the tasks list if not provided."""
        if self.tasks is None:
            self.tasks = []

    def add_task(self, task):
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def update_info(self, name=None, species=None, age=None):
        """Update the pet's information."""
        if name:
            self.name = name
        if species:
            self.species = species
        if age is not None:
            self.age = age

    def get_details(self):
        """Return a dictionary containing the pet's details."""
        return {'name': self.name, 'species': self.species, 'age': self.age}

@dataclass
class Task:
    name: str
    duration: int  # in minutes
    priority: int  # higher number = higher priority
    completed: bool = False

    def edit_task(self, name=None, duration=None, priority=None):
        """Edit the task's details."""
        if name:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority

    def check_constraints(self, available_time):
        """Check if the task can be scheduled within the available time."""
        return self.duration <= available_time

    def mark_complete(self):
        """Mark the task as complete."""
        self.completed = True

class Scheduler:
    def __init__(self, owner, pet, tasks=None):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []
        self.plan = []
        self.explanation = ""

    def generate_plan(self):
        """Generate a plan for the pet's tasks based on the owner's preferences."""
        available_time = self.owner.preferences.get('available_time', 24*60)  # default: all day
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        plan = []
        time_used = 0
        explanation = []
        for task in sorted_tasks:
            if time_used + task.duration <= available_time:
                plan.append(task)
                time_used += task.duration
                explanation.append(f"Added '{task.name}' (priority {task.priority}, {task.duration} min)")
            else:
                explanation.append(f"Skipped '{task.name}' (not enough time left)")
        self.plan = plan
        self.explanation = '\n'.join(explanation)
        return plan

    def explain_plan(self):
        """Explain the generated plan for the pet's tasks."""
        return self.explanation
