from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime, time, date
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
    care_preferences: List[str]
    owner: Optional['Owner'] = None
    type: str                           #type of pet
    
    def add_preferences(self, preference: str) -> None:
        """Add a care preference for the pet."""
        pass
    
    def remove_preference(self, preference: str) -> None:
        """Remove a care preference for the pet."""
        pass
    
    def needs_at_time(self, dt: datetime) -> List[str]:
        """Return list of required tasks at a given time."""
        pass


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
    
    def available_minutes(self) -> int:
        """Calculate total available minutes from all windows."""
        pass
    
    def window_available(self, duration: int, date: date) -> bool:
        """Check if a time window is available for the given duration on a date."""
        pass
    
    def deduct_time(self, duration: int, date: date) -> None:
        """Update availability by deducting time from a date."""
        pass
    
    def can_schedule(self, task: Task) -> bool:
        """Check if a task can be scheduled given current constraints."""
        pass
    
    def update_task(self, old_task: Task, new_task: Task) -> None:
        """Update an existing task with new values."""
        pass


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
        pass


@dataclass
class Schedule:
    """Represents a complete daily schedule for a pet."""
    pet: Pet
    owner: Owner
    plan_date: date
    entries: List[ScheduleEntry] = field(default_factory=list)
    unscheduled_tasks: List[Task] = field(default_factory=list)
    
    def generate_daily_plan(self, tasks: List[Task], pet: Pet, owner: Owner, date: date) -> None:
        """Generate a daily plan for a pet based on constraints."""
        pass
    
    def add_task(self) -> None:
        """Add a task to the schedule."""
        pass
    
    def remove_task(self) -> None:
        """Remove a task from the schedule."""
        pass
    
    def explain(self) -> List[str]:
        """Return reasoning for why tasks were scheduled or not scheduled."""
        pass
    
    def validate_conflicts(self) -> bool:
        """Validate schedule against pet preferences and owner constraints."""
        pass
