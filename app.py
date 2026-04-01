from datetime import date, time
from pawpal_system import Pet, Task, Owner, Priority, TimeWindow, Schedule
import streamlit as st

# Sample default owner setup for UI demo
if not isinstance(st.session_state.get("owner"), Owner):
    st.session_state.owner = Owner(
        name="Jordan",
        available_windows=[TimeWindow(start=time(8, 0), end=time(20, 0))],
        max_mins=240,
        pets=[],
    )

owner = st.session_state.owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.name = owner_name

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name:
        st.warning("Pet name cannot be empty.")
    else:
        existing = [p.name for p in owner.pets]
        if pet_name in existing:
            st.warning(f"Pet '{pet_name}' already exists.")
        else:
            new_pet = Pet(name=pet_name, age=1, species=species, health_conditions=[])
            owner.pets.append(new_pet)
            st.success(f"Added pet '{pet_name}' to owner {owner.name}.")

if owner.pets:
    selected_pet_name = st.selectbox("Choose a pet", [p.name for p in owner.pets])
    selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), owner.pets[0])
else:
    selected_pet = None

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not selected_pet:
        st.warning("Please add a pet first before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("Please add tasks first before generating a schedule.")
    else:
        task_objs = []
        for t in st.session_state.tasks:
            try:
                p_level = Priority[t["priority"].upper()]
            except KeyError:
                p_level = Priority.MEDIUM

            task_obj = Task(
                task_name=t["title"],
                description="User-defined task",
                duration=int(t["duration_minutes"]),
                priority=p_level,
                category="general",
            )
            task_objs.append(task_obj)

        schedule = Schedule(pet=selected_pet, owner=owner, plan_date=date.today())
        schedule.generate_daily_plan(tasks=task_objs)

        if schedule.entries:
            st.success(f"Schedule generated for {selected_pet.name}.")
            st.write("### Scheduled items")
            st.table([
                {
                    "task": e.task.task_name,
                    "start": e.starttime.strftime("%H:%M"),
                    "end": e.endtime.strftime("%H:%M"),
                }
                for e in schedule.entries
            ])
        else:
            st.warning("No tasks could be scheduled with the current constraints.")

        st.write("### Unscheduled tasks")
        if schedule.unscheduled_tasks:
            st.table([{"task": t.task_name} for t in schedule.unscheduled_tasks])
        else:
            st.info("All tasks fit in the schedule!")

