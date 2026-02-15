from dataclasses import dataclass
from datetime import datetime, timedelta

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
    time: str = None  # time of day for the task (e.g., "09:00", "14:30")
    recurrence: str = "none"  # recurrence type: "none", "daily", or "weekly"
    due_date: datetime = None  # the actual due date/time for the task

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
        """Mark the task as complete.

        Returns:
            Task or None: A new Task instance for the next occurrence if the task
                         is recurring (daily/weekly), otherwise None.
        """
        self.completed = True

        # If task is recurring, create a new instance for next occurrence
        if self.recurrence in ["daily", "weekly"]:
            # Calculate the next due date using timedelta
            next_due_date = None
            if self.due_date:
                if self.recurrence == "daily":
                    next_due_date = self.due_date + timedelta(days=1)
                elif self.recurrence == "weekly":
                    next_due_date = self.due_date + timedelta(days=7)
            else:
                # If no due_date was set, calculate from today
                base_date = datetime.now()
                if self.recurrence == "daily":
                    next_due_date = base_date + timedelta(days=1)
                elif self.recurrence == "weekly":
                    next_due_date = base_date + timedelta(days=7)

            new_task = Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                completed=False,
                time=self.time,
                recurrence=self.recurrence,
                due_date=next_due_date
            )
            return new_task

        return None

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

    def sort_by_time(self):
        """Sort tasks by their time attribute in chronological order.

        Returns a new list of tasks sorted by time. Tasks without a time
        attribute will be placed at the end of the list.
        """
        # Separate tasks with and without time
        tasks_with_time = [task for task in self.tasks if task.time is not None]
        tasks_without_time = [task for task in self.tasks if task.time is None]

        # Sort tasks with time chronologically
        sorted_tasks = sorted(tasks_with_time, key=lambda t: t.time)

        # Append tasks without time at the end
        return sorted_tasks + tasks_without_time

    def filter_tasks(self, completed=None, pet_name=None):
        """Filter tasks by completion status and/or pet name.

        Args:
            completed (bool, optional): Filter by completion status.
                                       True for completed tasks, False for incomplete.
                                       None returns all tasks.
            pet_name (str, optional): Filter by pet name. If provided, only returns
                                     tasks if the scheduler's pet name matches.

        Returns:
            list: Filtered list of Task objects matching the criteria.
        """
        filtered = self.tasks

        # Filter by pet name if provided
        if pet_name is not None:
            if self.pet.name.lower() != pet_name.lower():
                return []  # No tasks match if pet name doesn't match

        # Filter by completion status if provided
        if completed is not None:
            filtered = [task for task in filtered if task.completed == completed]

        return filtered

    def complete_task(self, task):
        """Mark a task as complete and handle recurring tasks automatically.

        If the task is recurring (daily or weekly), this method will automatically
        create a new instance for the next occurrence and add it to the scheduler.

        Args:
            task (Task): The task to mark as complete.

        Returns:
            Task or None: The new recurring task instance if created, otherwise None.
        """
        new_task = task.mark_complete()

        # If a new recurring task was created, add it to the scheduler
        if new_task is not None:
            self.tasks.append(new_task)
            # Also add to pet's task list if it exists
            if hasattr(self.pet, 'tasks'):
                self.pet.add_task(new_task)

        return new_task

    def detect_conflicts(self):
        """Detect if two or more tasks are scheduled at overlapping times.

        This method checks for time conflicts between tasks. Two tasks conflict if:
        1. They both have due_date values set
        2. Their time ranges overlap (considering start time + duration)

        Returns:
            list: A list of tuples, where each tuple contains two conflicting Task objects.
                 Returns an empty list if no conflicts are found.
        """
        conflicts = []

        # Get tasks that have due dates
        tasks_with_dates = [task for task in self.tasks if task.due_date is not None]

        # Compare each pair of tasks
        for i in range(len(tasks_with_dates)):
            task1 = tasks_with_dates[i]
            task1_start = task1.due_date
            task1_end = task1_start + timedelta(minutes=task1.duration)

            for j in range(i + 1, len(tasks_with_dates)):
                task2 = tasks_with_dates[j]
                task2_start = task2.due_date
                task2_end = task2_start + timedelta(minutes=task2.duration)

                # Check if the time ranges overlap
                # Tasks overlap if: task1 starts before task2 ends AND task1 ends after task2 starts
                if task1_start < task2_end and task1_end > task2_start:
                    conflicts.append((task1, task2))

        return conflicts
