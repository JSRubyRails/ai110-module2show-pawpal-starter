"""Tests for PawPal+ core behaviors."""

import os
import sys

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Task


def test_task_completion_changes_status():
    """Calling mark_complete() should change the task's status to complete."""
    task = Task("Morning walk", duration_minutes=30)

    # Starts out not complete.
    assert task.status == "pending"
    assert task.is_complete() is False

    task.mark_complete()

    # Status actually changed.
    assert task.status == "complete"
    assert task.is_complete() is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count by one."""
    pet = Pet("Mochi", species="dog")

    assert len(pet.list_tasks()) == 0

    pet.add_task(Task("Breakfast", duration_minutes=10))

    assert len(pet.list_tasks()) == 1
