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

    # Add tasks OUT OF ORDER (low priority first, then high, mixed durations)
    dog.tasks.append(Task(
        task_name="Flea Treatment",
        description="Apply monthly flea treatment",
        duration=10,
        priority=Priority.LOW,
        category="health",
        frequency="once",
        required_for_species=["dog"],
        completed=True,  # already done — used to test filtering
    ))

    dog.tasks.append(Task(
        task_name="Vet Checkup",
        description="Take both pets to the veterinarian",
        duration=60,
        priority=Priority.MEDIUM,
        category="health",
        frequency="once",
        required_for_species=["dog", "cat"],
    ))

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
        task_name="Groom Cat",
        description="Brush whiskers and fur",
        duration=20,
        priority=Priority.LOW,
        category="grooming",
        frequency="weekly",
        required_for_species=["cat"],
    ))

    cat.tasks.append(Task(
        task_name="Clean Litter Box",
        description="Scoop and refresh litter box",
        duration=10,
        priority=Priority.HIGH,
        category="hygiene",
        frequency="daily",
        required_for_species=["cat"],
        completed=True,  # already done — used to test filtering
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

    # ------------------------------------------------------------------ #
    #  Generate schedules (generate_daily_plan sorts internally by pri)   #
    # ------------------------------------------------------------------ #
    today = date.today()
    schedules: dict[str, Schedule] = {}

    for pet in owner.pets:
        schedule = Schedule(pet=pet, owner=owner, plan_date=today)
        schedule.generate_daily_plan()
        schedules[pet.name] = schedule

    # ------------------------------------------------------------------ #
    #  Print full daily schedule                                           #
    # ------------------------------------------------------------------ #
    print("=" * 50)
    print(f"PAWPAL — Daily Schedule for {owner.name}  ({today})")
    print("=" * 50)

    for pet in owner.pets:
        sched = schedules[pet.name]
        print(f"\nPet: {pet.name} ({pet.species})")
        print("-" * 40)

        if sched.entries:
            for entry in sched.entries:
                status = "DONE" if entry.task.completed else "pending"
                print(f"  [{status:7}] {entry.task.task_name:20} {entry.starttime.strftime('%H:%M')}–{entry.endtime.strftime('%H:%M')}  ({entry.task.priority.value})")
        else:
            print("  (no tasks scheduled)")

        if sched.unscheduled_tasks:
            print("  Unscheduled:")
            for ut in sched.unscheduled_tasks:
                print(f"    * {ut.task_name} ({ut.duration} min, {ut.priority.value})")

    # ------------------------------------------------------------------ #
    #  Demo: Schedule.filter_tasks — filter by completion status          #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 50)
    print("FILTER DEMO — Schedule.filter_tasks()")
    print("=" * 50)

    for pet in owner.pets:
        sched = schedules[pet.name]

        pending  = sched.filter_tasks(completed=False)
        done     = sched.filter_tasks(completed=True)
        all_     = sched.filter_tasks()

        print(f"\n{pet.name}:")
        print(f"  All tasks  ({len(all_):2}): {[t.task_name for t in all_]}")
        print(f"  Pending    ({len(pending):2}): {[t.task_name for t in pending]}")
        print(f"  Completed  ({len(done):2}): {[t.task_name for t in done]}")

    # ------------------------------------------------------------------ #
    #  Demo: Owner.filter_tasks — filter by pet name and/or completion    #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 50)
    print("FILTER DEMO — Owner.filter_tasks()")
    print("=" * 50)

    # All tasks for Fido only
    fido_tasks = owner.filter_tasks(pet_name="Fido")
    print(f"\nAll tasks for Fido ({len(fido_tasks)}):")
    for pet, task in fido_tasks:
        status = "done" if task.completed else "pending"
        print(f"  [{status}] {task.task_name} ({task.priority.value})")

    # All incomplete tasks across every pet
    all_pending = owner.filter_tasks(completed=False)
    print(f"\nAll PENDING tasks across all pets ({len(all_pending)}):")
    for pet, task in all_pending:
        print(f"  {pet.name:10} {task.task_name} ({task.priority.value})")

    # All completed tasks across every pet
    all_done = owner.filter_tasks(completed=True)
    print(f"\nAll COMPLETED tasks across all pets ({len(all_done)}):")
    for pet, task in all_done:
        print(f"  {pet.name:10} {task.task_name} ({task.priority.value})")

    # Combine: completed tasks for Whiskers only
    cat_done = owner.filter_tasks(pet_name="Whiskers", completed=True)
    print(f"\nCompleted tasks for Whiskers only ({len(cat_done)}):")
    for pet, task in cat_done:
        print(f"  {task.task_name} ({task.priority.value})")


if __name__ == "__main__":
    main()
