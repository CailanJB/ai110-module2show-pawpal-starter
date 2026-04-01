from datetime import datetime

import pytest

from pawpal_system import Pet, Task, Priority


def test_mark_complete_sets_status_and_timestamp():
    task = Task(
        task_name="Walk",
        description="Take the dog for a walk",
        duration=30,
        priority=Priority.MEDIUM,
        category="exercise",
    )

    assert task.completed is False
    assert task.last_completed is None

    task.mark_complete()

    assert task.completed is True
    assert isinstance(task.last_completed, datetime)


def test_adding_task_to_pet_increments_task_count():
    pet = Pet(name="Buddy", age=4, species="dog", health_conditions=[])
    initial_count = len(pet.tasks)

    task = Task(
        task_name="Brush",
        description="Brush the pet's fur",
        duration=15,
        priority=Priority.LOW,
        category="grooming",
    )

    pet.tasks.append(task)

    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] is task
