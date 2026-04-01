from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional


@dataclass
class Task:
    task_name: str
    duration: int  # minutes
    priority: int
    category: str


@dataclass
class Pet:
    name: str
    age: int
    species: str
    health_conditions: str
    care_preferences: List[str] = field(default_factory=list)

    def add_preference(self, preference: str):
        self.care_preferences.append(preference)

    def remove_preference(self, preference: str):
        if preference in self.care_preferences:
            self.care_preferences.remove(preference)

    def needs_at_time(self, dt: datetime) -> List[Task]:
        # TODO: return tasks that are due/needed at dt
        return []


@dataclass
class AvailableWindow:
    starttime: datetime
    endtime: datetime

    def update_window(self, window: "AvailableWindow"):
        self.starttime = window.starttime
        self.endtime = window.endtime

    def overlap(self, window: "AvailableWindow") -> bool:
        return not (self.endtime <= window.starttime or self.starttime >= window.endtime)


class Owner:
    def __init__(self, name: str, available_windows: List[AvailableWindow], max_mins: int):
        self.name = name
        self.available_windows = available_windows
        self.max_mins = max_mins

    def available_minutes(self, date_obj: date) -> int:
        # TODO: compute total minutes free for date_obj
        return 0

    def window_available(self, duration: int, date_obj: date) -> bool:
        # TODO: check if any available window can fit duration
        return False

    def deduct_time(self, duration: int, date_obj: date):
        # TODO: reduce available windows by duration
        pass

    def can_schedule(self, task: Task) -> bool:
        # TODO: validate task against preferences, max_mins, availability
        return False


class Schedule:
    def __init__(self, task: Optional[Task] = None,
                 starttime: Optional[datetime] = None,
                 endtime: Optional[datetime] = None):
        self.task = task
        self.starttime = starttime
        self.endtime = endtime

    def fit_task(self, task: Task) -> bool:
        if self.starttime is None or self.endtime is None:
            return False
        available_mins = int((self.endtime - self.starttime).total_seconds() // 60)
        return task.duration <= available_mins

    def generate_daily_plan(self, tasks: List[Task], pet: Pet, owner: Owner, plan_date: date):
        # TODO: schedule tasks for one day
        pass

    def add_task(self, task: Task):
        # TODO: assign task to this schedule
        self.task = task

    def remove_task(self, task: Task):
        # TODO: remove task if assigned
        if self.task == task:
            self.task = None
            self.starttime = None
            self.endtime = None
