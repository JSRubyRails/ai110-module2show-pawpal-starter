import streamlit as st
from pawpalsystem import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ========== SESSION STATE INITIALIZATION ==========
def initialize_session_state():
    """Initialize all session state objects if they don't exist.
    This ensures objects are created once and persist across reruns."""

    # Initialize Owner if it does not exist
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Jordan", preferences={"available_time": 180})

    # Initialize Pet if it does not exist
    if "pet" not in st.session_state:
        st.session_state.pet = Pet(name="Mochi", species="dog", age=3)

    # Initialize Scheduler if it does not exist (requires owner and pet)
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=st.session_state.pet
        )

    # Initialize task objects list if it does not exist
    if "task_objects" not in st.session_state:
        st.session_state.task_objects = []

    # Initialize tasks dictionary list for UI (separate from task_objects)
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

# Call initialization function
initialize_session_state()

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

st.subheader("Pet & Owner Info")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Owner**")
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
    available_time = st.number_input(
        "Available time (minutes)",
        min_value=0,
        max_value=1440,
        value=st.session_state.owner.preferences.get('available_time', 180)
    )
    if st.button("Update Owner"):
        # Use update_preferences() method from Owner class
        st.session_state.owner.name = owner_name
        st.session_state.owner.update_preferences({"available_time": available_time})
        st.success(f"✅ Updated owner: {owner_name}")

with col2:
    st.markdown("**Pet**")
    pet_name = st.text_input("Pet name", value=st.session_state.pet.name)
    species = st.selectbox(
        "Species",
        ["dog", "cat", "other"],
        index=["dog", "cat", "other"].index(st.session_state.pet.species)
    )
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=st.session_state.pet.age)
    if st.button("Update Pet"):
        # Use update_info() method from Pet class
        st.session_state.pet.update_info(name=pet_name, species=species, age=pet_age)
        st.success(f"✅ Updated pet: {pet_name}")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    # Map priority strings to numeric values (higher = more important)
    priority_options = {"low": 1, "medium": 2, "high": 3}
    priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    # Create a Task object
    priority_value = priority_options[priority_str]
    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority_value
    )

    # Use the add_task() method from Pet class
    st.session_state.pet.add_task(new_task)

    # Also add to scheduler's task list
    st.session_state.scheduler.tasks.append(new_task)

    # Keep UI-friendly dictionary for display table
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority_str}
    )

    st.success(f"✅ Added '{task_title}' to {st.session_state.pet.name}'s tasks!")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Click to generate a schedule based on priority and available time.")

if st.button("Generate schedule"):
    if len(st.session_state.scheduler.tasks) == 0:
        st.warning("⚠️ No tasks to schedule. Add some tasks first!")
    else:
        # Use the generate_plan() method from Scheduler class
        plan = st.session_state.scheduler.generate_plan()

        # Use the explain_plan() method to get the explanation
        explanation = st.session_state.scheduler.explain_plan()

        st.success(f"✅ Schedule generated for {st.session_state.pet.name}!")

        # Display the plan
        st.markdown("### 📋 Generated Schedule")
        if plan:
            plan_data = []
            for task in plan:
                plan_data.append({
                    "Task": task.name,
                    "Duration (min)": task.duration,
                    "Priority": task.priority,
                    "Status": "✓ Scheduled"
                })
            st.table(plan_data)

            # Show total time
            total_time = sum(task.duration for task in plan)
            available_time = st.session_state.owner.preferences.get('available_time', 0)
            st.info(f"⏱️ Total scheduled time: {total_time} minutes out of {available_time} minutes available")
        else:
            st.warning("No tasks could be scheduled.")

        # Display the explanation
        st.markdown("### 💡 Explanation")
        st.text(explanation)

st.divider()

# ========== SESSION STATE DEBUG SECTION ==========
with st.expander("🔍 Session State Debug Info", expanded=False):
    st.caption("View what's currently stored in session state")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Session State Keys:**")
        st.write(list(st.session_state.keys()))

    with col2:
        st.markdown("**Object Types:**")
        for key in st.session_state.keys():
            st.write(f"- `{key}`: {type(st.session_state[key]).__name__}")

    st.markdown("**Owner Object (using get_info() method):**")
    if "owner" in st.session_state:
        owner_info = st.session_state.owner.get_info()
        st.write(owner_info)

    st.markdown("**Pet Object (using get_details() method):**")
    if "pet" in st.session_state:
        pet_details = st.session_state.pet.get_details()
        st.write(pet_details)
        st.write(f"Tasks assigned: {len(st.session_state.pet.tasks)}")

    st.markdown("**Full Session State:**")
    st.json({k: str(v) for k, v in st.session_state.items()})
