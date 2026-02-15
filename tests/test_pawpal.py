import pytest
from pawpal_system import Task, Pet

def test_task_completion():
    task = Task(name="Feed", duration=10, priority=1)
    assert not task.completed
    task.mark_complete()
    assert task.completed

def test_task_addition():
    pet = Pet(name="Buddy", species="Dog", age=5)
    initial_count = len(pet.tasks)
    task = Task(name="Walk", duration=30, priority=2)
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] == task
