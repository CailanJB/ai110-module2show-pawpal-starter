from datetime import date, time

from pawpal_system import Owner, Pet, Task, TimeWindow, Priority, Schedule


def main() -> None:
    # Create owner with availability windows (morning and afternoon)
    owner = Owner(
        name="Alex",
        available_windows=[
            TimeWindow(start=time(8, 0), end=time(12, 0)),
            TimeWindow(start=time(13, 0), end=time(18, 0)),
        ],
        max_mins=120,
    )

    # Create two pets
    dog = Pet(name="Fido", age=4, species="dog", health_conditions=["healthy"], care_preferences=["walk in morning", "food in evening"], owner=owner)
    cat = Pet(name="Whiskers", age=2, species="cat", health_conditions=["healthy"], care_preferences=["food in afternoon", "litter cleanup"], owner=owner)

    owner.pets.extend([dog, cat])

    # Add tasks (different durations/priorities/species requirements)
    dog.tasks.append(Task(
        task_name="Morning Walk",
        description="Walk the dog around the block",
        duration=30,
        priority=Priority.HIGH,
        category="exercise",
        frequency="daily",
        required_for_species=["dog"],
    ))

    dog.tasks.append(Task(
        task_name="Feed Dog",
        description="Feed Fido breakfast",
        duration=15,
        priority=Priority.HIGH,
        category="feeding",
        frequency="daily",
        required_for_species=["dog"],
    ))

    cat.tasks.append(Task(
        task_name="Feed Cat",
        description="Feed Whiskers lunch",
        duration=10,
        priority=Priority.MEDIUM,
        category="feeding",
        frequency="daily",
        required_for_species=["cat"],
    ))

    cat.tasks.append(Task(
        task_name="Groom Cat",
        description="Brush whiskers and fur",
        duration=20,
        priority=Priority.LOW,
        category="grooming",
        frequency="weekly",
        required_for_species=["cat"],
    ))

    # Add a cross-pet task (one-time for both pets)
    owner_shared_task = Task(
        task_name="Vet Checkup",
        description="Take both pets to the veterinarian",
        duration=60,
        priority=Priority.MEDIUM,
        category="health",
        frequency="once",
        required_for_species=["dog", "cat"],
    )

    dog.tasks.append(owner_shared_task)

    # Generate today's schedule for each pet and print
    today = date.today()

    print("Today's Schedule for Pet Owner:")
    print("Owner:", owner.name)
    print("Date:", today)
    print("============\n")

    for pet in owner.pets:
        schedule = Schedule(pet=pet, owner=owner, plan_date=today)
        schedule.generate_daily_plan()

        print(f"Pet: {pet.name} ({pet.species})")

        if schedule.entries:
            for entry in schedule.entries:
                print(f"  - {entry.task.task_name} from {entry.starttime.strftime('%H:%M')} to {entry.endtime.strftime('%H:%M')} ({entry.task.priority.value})")
        else:
            print("  - No tasks scheduled")

        if schedule.unscheduled_tasks:
            print("  Unscheduled tasks:")
            for ut in schedule.unscheduled_tasks:
                print(f"    * {ut.task_name} ({ut.duration} min, {ut.priority.value})")

        print("")


if __name__ == "__main__":
    main()
