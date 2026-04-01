from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime, time, date, timedelta
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TimeWindow:
    """Represents a time window with start and end times."""
    start: time
    end: time


@dataclass
class Pet:
    """Represents a pet with its attributes and care preferences."""
    name: str
    age: int
    species: str
    health_conditions: List[str]
    care_preferences: List[str] = field(default_factory=list)
    owner: Optional['Owner'] = None
    type: str = "unknown"                           # type of pet
    tasks: List['Task'] = field(default_factory=list)

    def add_preferences(self, preference: str) -> None:
        """Add a care preference for the pet."""
        normalized = preference.strip().lower()
        if normalized and normalized not in [p.lower() for p in self.care_preferences]:
            self.care_preferences.append(preference.strip())

    def remove_preference(self, preference: str) -> None:
        """Remove a care preference for the pet."""
        normalized = preference.strip().lower()
        self.care_preferences = [p for p in self.care_preferences if p.strip().lower() != normalized]

    def needs_at_time(self, dt: datetime) -> List[str]:
        """Return list of required tasks at a given time."""
        active_needs = []
        hour = dt.hour

        # Time of day categories
        if 4 <= hour < 12:
            target = "morning"
        elif 12 <= hour < 17:
            target = "afternoon"
        elif 17 <= hour < 21:
            target = "evening"
        else:
            target = "night"

        for pref in self.care_preferences:
            lower = pref.lower()
            if target in lower or "all day" in lower or "anytime" in lower:
                active_needs.append(pref)

        # Fallback: if no time-specific preferences, return all
        if not active_needs:
            active_needs = list(self.care_preferences)

        return active_needs


@dataclass
class Task:
    """Represents a pet care task with its properties."""
    task_name: str
    description: str
    duration: int
    priority: Priority
    category: str
    frequency: str = "once"  # "once", "daily", "weekly"
    preferred_time: Optional[TimeWindow] = None  # ideal time window, optional
    required_for_species: List[str] = field(default_factory=list)  # ["dog", "cat"]
    repeat_count: int = 1  # number of repeats if recurring
    completed: bool = False
    last_completed: Optional[datetime] = None

    def mark_complete(self, completed_at: Optional[datetime] = None) -> None:
        """Mark this task as completed and optionally record completion time."""
        self.completed = True
        self.last_completed = completed_at or datetime.now()

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete so it can be rescheduled."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Check if the task is recurring based on frequency or repeat_count."""
        return self.frequency.lower() in {"daily", "weekly"} or self.repeat_count > 1

    def next_due_status(self, reference: Optional[datetime] = None) -> str:
        """Return a human-friendly due status for this task."""
        if not reference:
            reference = datetime.now()

        if self.completed and self.last_completed:
            if self.frequency.lower() == "daily":
                return "due tomorrow" if reference.date() == self.last_completed.date() else "due today"
            if self.frequency.lower() == "weekly":
                delta = (reference.date() - self.last_completed.date()).days
                return "due soon" if delta >= 6 else "up to date"
            return "completed"

        if self.frequency.lower() == "once":
            return "pending"

        return "pending recurring"

    def is_due(self, reference: Optional[datetime] = None) -> bool:
        """Determine whether this task should be prepared for scheduling at a moment."""
        if not reference:
            reference = datetime.now()

        if self.frequency.lower() == "once":
            return not self.completed

        if self.last_completed is None:
            return True

        if self.frequency.lower() == "daily":
            return reference.date() > self.last_completed.date()

        if self.frequency.lower() == "weekly":
            return (reference.date() - self.last_completed.date()).days >= 7

        return True


@dataclass
class Owner:
    """Represents the pet owner with availability and scheduling constraints."""
    name: str
    available_windows: List[TimeWindow]
    max_mins: int
    pets: List[Pet] = field(default_factory=list)
    work_hours: Optional[TimeWindow] = None  # e.g., 9-5 unavailable
    booked_minutes_by_date: dict = field(default_factory=dict)

    def available_minutes(self) -> int:
        """Calculate total available minutes from all windows for today (no booked time)."""
        total = 0
        for window in self.available_windows:
            minutes = int((datetime.combine(date.min, window.end) - datetime.combine(date.min, window.start)).total_seconds() / 60)
            total += max(0, minutes)
        return total

    def _occupied_minutes(self, date_obj: date) -> int:
        return int(self.booked_minutes_by_date.get(date_obj.isoformat(), 0))

    def window_available(self, duration: int, date: date) -> bool:
        """Check if a time window is available for the given duration on a date."""
        if duration <= 0:
            return False

        remaining = self.available_minutes() - self._occupied_minutes(date)
        if remaining < duration:
            return False

        for w in self.available_windows:
            window_length = int((datetime.combine(date.min, w.end) - datetime.combine(date.min, w.start)).total_seconds() / 60)
            if window_length >= duration:
                if self.work_hours:
                    work_length = int((datetime.combine(date.min, self.work_hours.end) - datetime.combine(date.min, self.work_hours.start)).total_seconds() / 60)
                    if window_length - work_length < duration:
                        continue
                return True

        return False

    def deduct_time(self, duration: int, date: date) -> None:
        """Update availability by deducting time from a date."""
        if duration <= 0:
            return
        key = date.isoformat()
        self.booked_minutes_by_date[key] = self.booked_minutes_by_date.get(key, 0) + duration

    def can_schedule(self, task: Task) -> bool:
        """Check if a task can be scheduled given current constraints."""
        if task.duration > self.max_mins:
            return False

        if task.frequency.lower() == "once" and task.completed:
            return False

        return self.window_available(task.duration, date.today())

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Tuple[Pet, Task]]:
        """Return (pet, task) pairs matching the given filters across all owned pets.

        Args:
            completed: If provided, only return tasks whose completed flag matches.
            pet_name: If provided, only return tasks belonging to the pet with this name
                      (case-insensitive).

        Returns:
            A list of (Pet, Task) tuples for every matching task.
        """
        results: List[Tuple[Pet, Task]] = []
        for pet in self.pets:
            if pet_name is not None and pet.name.lower() != pet_name.strip().lower():
                continue
            for task in pet.tasks:
                if completed is None or task.completed == completed:
                    results.append((pet, task))
        return results

    def update_task(self, old_task: Task, new_task: Task) -> None:
        """Update an existing task with new values."""
        old_task.task_name = new_task.task_name
        old_task.description = new_task.description
        old_task.duration = new_task.duration
        old_task.priority = new_task.priority
        old_task.category = new_task.category
        old_task.frequency = new_task.frequency
        old_task.preferred_time = new_task.preferred_time
        old_task.required_for_species = list(new_task.required_for_species)
        old_task.repeat_count = new_task.repeat_count
        old_task.completed = new_task.completed
        old_task.last_completed = new_task.last_completed


@dataclass
class ScheduleEntry:
    """Represents a single task within a daily schedule."""
    task: Task
    starttime: time
    endtime: time
    completed: bool = False
    actual_start: Optional[time] = None
    actual_end: Optional[time] = None

    def fit_task(self, task: Task) -> bool:
        """Check if a task can fit in this time slot."""
        duration_minutes = task.duration
        slot_length = int((datetime.combine(date.min, self.endtime) - datetime.combine(date.min, self.starttime)).total_seconds() / 60)
        return duration_minutes <= slot_length


@dataclass
class Schedule:
    """Represents a complete daily schedule for a pet."""
    pet: Pet
    owner: Owner
    plan_date: date
    entries: List[ScheduleEntry] = field(default_factory=list)
    unscheduled_tasks: List[Task] = field(default_factory=list)

    def generate_daily_plan(self, tasks: Optional[List[Task]] = None, pet: Optional[Pet] = None, owner: Optional[Owner] = None, plan_date: Optional[date] = None) -> None:
        """Generate a daily plan for a pet based on constraints."""
        self.entries.clear()
        self.unscheduled_tasks.clear()

        if pet is not None:
            self.pet = pet
        if owner is not None:
            self.owner = owner
        if plan_date is not None:
            self.plan_date = plan_date

        tasks_to_schedule = tasks if tasks is not None else self.pet.tasks

        # Collect tasks for this pet only
        tasks_to_schedule = [task for task in tasks_to_schedule if (not task.required_for_species or self.pet.species in task.required_for_species)]

        # Sort by priority and duration
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        tasks_to_schedule.sort(key=lambda t: (priority_order.get(t.priority, 2), t.duration))

        window_cursor = 0
        sorted_windows = sorted(self.owner.available_windows, key=lambda w: w.start)

        for task in tasks_to_schedule:
            if not task.is_due(reference=datetime.combine(self.plan_date, time.min)):
                self.unscheduled_tasks.append(task)
                continue

            if task.completed and task.frequency.lower() == "once":
                continue

            if task.duration <= 0 or task.duration > self.owner.max_mins:
                self.unscheduled_tasks.append(task)
                continue

            scheduled = False
            for window in sorted_windows[window_cursor:]:
                filled = [entry for entry in self.entries if entry.starttime >= window.start and entry.endtime <= window.end]
                start_time = window.start
                if filled:
                    # Move to end of the last scheduled task in this window
                    start_time = max(start_time, max(entry.endtime for entry in filled))

                remaining_minutes = int((datetime.combine(date.min, window.end) - datetime.combine(date.min, start_time)).total_seconds() / 60)
                if remaining_minutes >= task.duration:
                    end_time = (datetime.combine(date.min, start_time) + timedelta(minutes=task.duration)).time()
                    entry = ScheduleEntry(task=task, starttime=start_time, endtime=end_time)
                    if entry.fit_task(task):
                        self.entries.append(entry)
                        self.owner.deduct_time(task.duration, self.plan_date)
                        scheduled = True
                        break

                window_cursor += 1

            if not scheduled:
                self.unscheduled_tasks.append(task)

    def add_task(self, task: Task) -> bool:
        """Add a task to the schedule if it fits."""
        if not self.owner.can_schedule(task):
            self.unscheduled_tasks.append(task)
            return False

        self.generate_daily_plan(tasks=self.pet.tasks + [task])
        return task not in self.unscheduled_tasks

    def remove_task(self, task: Task) -> bool:
        """Remove a task from the schedule entries."""
        for entry in self.entries:
            if entry.task is task or entry.task.task_name == task.task_name:
                self.entries.remove(entry)
                # restore owner's booked time conservatively
                self.owner.booked_minutes_by_date[self.plan_date.isoformat()] = max(0, self.owner.booked_minutes_by_date.get(self.plan_date.isoformat(), 0) - task.duration)
                return True
        if task in self.unscheduled_tasks:
            self.unscheduled_tasks.remove(task)
            return True
        return False

    def explain(self) -> List[str]:
        """Return reasoning for why tasks were scheduled or not scheduled."""
        explanation = []
        for entry in self.entries:
            explanation.append(f"Scheduled '{entry.task.task_name}' for {self.pet.name} from {entry.starttime.strftime('%H:%M')} to {entry.endtime.strftime('%H:%M')}. ")
        for task in self.unscheduled_tasks:
            explanation.append(f"Could not schedule '{task.task_name}' for {self.pet.name} (duration {task.duration} min). ")
        return explanation

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks matching the given filters.

        Args:
            completed: If provided, only return tasks whose completed flag matches.
            pet_name: If provided, only return tasks when this schedule's pet name matches
                      (case-insensitive). Returns an empty list if the pet doesn't match.

        Returns:
            A flat list of matching Task objects from both scheduled entries and
            unscheduled_tasks.
        """
        if pet_name is not None and self.pet.name.lower() != pet_name.strip().lower():
            return []

        all_tasks = [entry.task for entry in self.entries] + list(self.unscheduled_tasks)

        if completed is None:
            return all_tasks

        return [task for task in all_tasks if task.completed == completed]

    def validate_conflicts(self) -> bool:
        """Validate schedule against pet preferences and owner constraints."""
        # Check for overlapping entries
        sorted_entries = sorted(self.entries, key=lambda e: e.starttime)
        for i in range(len(sorted_entries) - 1):
            if sorted_entries[i].endtime > sorted_entries[i + 1].starttime:
                return False

        # Ensure total time doesn't exceed available minutes
        total = sum(entry.task.duration for entry in self.entries)
        if total > self.owner.available_minutes():
            return False

        return True

