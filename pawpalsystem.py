from dataclasses import dataclass

class Owner:
    def __init__(self, name, preferences=None):
        self.name = name
        self.preferences = preferences or {}

    def update_preferences(self):
        pass

    def get_info(self):
        pass

@dataclass
class Pet:
    name: str
    species: str
    age: int

    def update_info(self):
        pass

    def get_details(self):
        pass

@dataclass
class Task:
    name: str
    duration: int
    priority: int

    def edit_task(self):
        pass

    def check_constraints(self):
        pass

class Scheduler:
    def __init__(self, owner, pet, tasks=None):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []

    def generate_plan(self):
        pass

    def explain_plan(self):
        pass
