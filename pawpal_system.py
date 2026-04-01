from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
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
    tasks: List[Task] = field(default_factory=list)

    def add_preference(self, preference: str):
        self.care_preferences.append(preference)

    def remove_preference(self, preference: str):
        if preference in self.care_preferences:
            self.care_preferences.remove(preference)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def needs_at_time(self, dt: datetime) -> List[Task]:
        # TODO: return tasks that are due/needed at dt (if tasks are timed)
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

    def duration_minutes(self) -> int:
        return int((self.endtime - self.starttime).total_seconds() // 60)


class Owner:
    def __init__(self, name: str, available_windows: List[AvailableWindow], max_mins: int):
        self.name = name
        self.available_windows = available_windows
        self.max_mins = max_mins
        self.scheduled_tasks: List[Task] = []

    def available_minutes(self, date_obj: date) -> int:
        # currently does not filter by date, assumes windows are for this day
        return sum(w.duration_minutes() for w in self.available_windows)

    def window_available(self, duration: int, date_obj: date) -> bool:
        return any(w.duration_minutes() >= duration for w in self.available_windows)

    def deduct_time(self, duration: int, date_obj: date):
        # simple deduct from first-fitting window
        for w in self.available_windows:
            if w.duration_minutes() >= duration:
                w.starttime += timedelta(minutes=duration)
                if w.starttime >= w.endtime:
                    self.available_windows.remove(w)
                return

    def can_schedule(self, task: Task) -> bool:
        if task.duration > self.max_mins:
            return False
        return self.window_available(task.duration, date.today())

    def schedule_task(self, task: Task):
        self.scheduled_tasks.append(task)


@dataclass
class ScheduleEntry:
    task: Task
    starttime: datetime
    endtime: datetime
    def duration_minutes(self) -> int:
        return int((self.endtime - self.starttime).total_seconds() // 60)


@dataclass
class DailyPlan:
    date: date
    entries: List[ScheduleEntry] = field(default_factory=list)
    unassigned_tasks: List[Task] = field(default_factory=list)

    def add_entry(self, entry: ScheduleEntry):
        self.entries.append(entry)

    def total_duration(self) -> int:
        return sum(entry.duration_minutes() for entry in self.entries)

    def add_unassigned(self, task: Task):
        self.unassigned_tasks.append(task)

    def is_overbooked(self) -> bool:
        return False


class PawPalScheduler:
    @staticmethod
    def generate_daily_plan(tasks: List[Task], pet: Pet, owner: Owner, plan_date: date) -> DailyPlan:
        plan = DailyPlan(date=plan_date)
        sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.duration))

        for task in sorted_tasks:
            if not owner.can_schedule(task):
                plan.add_unassigned(task)
                continue

            # place task at first available window start
            window = next((w for w in owner.available_windows if w.duration_minutes() >= task.duration), None)
            if not window:
                plan.add_unassigned(task)
                continue

            start = window.starttime
            end = start + timedelta(minutes=task.duration)
            plan.add_entry(ScheduleEntry(task=task, starttime=start, endtime=end))

            owner.deduct_time(task.duration, plan_date)
            owner.schedule_task(task)

        return plan

    @staticmethod
    def explain_plan(plan: DailyPlan) -> List[str]:
        explanation = []
        for entry in plan.entries:
            explanation.append(
                f"{entry.task.task_name} scheduled {entry.starttime.strftime('%H:%M')} - {entry.endtime.strftime('%H:%M')} "
                f"(priority={entry.task.priority})"
            )
        for task in plan.unassigned_tasks:
            explanation.append(f"Could not schedule {task.task_name} (priority={task.priority})")
        return explanation

