import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime

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

# Additional task options (time and recurrence)
col4, col5 = st.columns(2)
with col4:
    time_of_day = st.text_input("Time of day (optional, e.g., 09:00)", value="", placeholder="HH:MM")
with col5:
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"], index=0)

if st.button("Add task"):
    # Create a Task object
    priority_value = priority_options[priority_str]

    # Calculate due_date if time is provided
    due_date = None
    if time_of_day:
        try:
            # Parse the time and combine with today's date
            time_parts = time_of_day.split(":")
            if len(time_parts) == 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                due_date = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        except (ValueError, IndexError):
            st.warning("⚠️ Invalid time format. Use HH:MM (e.g., 09:00)")

    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=priority_value,
        time=time_of_day if time_of_day else None,
        recurrence=recurrence,
        due_date=due_date
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
    st.write("**Current tasks:**")

    # Add filter options
    col1, col2 = st.columns(2)
    with col1:
        show_completed = st.checkbox("Show completed tasks", value=True)
    with col2:
        sort_by_time = st.checkbox("Sort by time", value=False)

    # Use Scheduler's filter_tasks method
    if show_completed:
        filtered_tasks = st.session_state.scheduler.tasks
    else:
        filtered_tasks = st.session_state.scheduler.filter_tasks(completed=False)

    # Use Scheduler's sort_by_time method
    if sort_by_time:
        display_tasks = st.session_state.scheduler.sort_by_time()
        # Filter the sorted tasks if needed
        if not show_completed:
            display_tasks = [t for t in display_tasks if not t.completed]
    else:
        display_tasks = filtered_tasks

    # Display tasks in a professional table
    if display_tasks:
        task_data = []
        priority_map = {1: "Low", 2: "Medium", 3: "High"}
        for task in display_tasks:
            task_data.append({
                "Task": task.name,
                "Duration (min)": task.duration,
                "Priority": priority_map.get(task.priority, task.priority),
                "Time": task.time if task.time else "Not scheduled",
                "Status": "✓ Complete" if task.completed else "○ Pending"
            })
        st.table(task_data)

        # Show summary
        completed_count = sum(1 for t in st.session_state.scheduler.tasks if t.completed)
        total_count = len(st.session_state.scheduler.tasks)
        st.success(f"📊 {completed_count}/{total_count} tasks completed")
    else:
        st.info("No tasks match the current filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ========== MARK TASKS COMPLETE ==========
st.subheader("✓ Complete Tasks")

if st.session_state.scheduler.tasks:
    incomplete_tasks = st.session_state.scheduler.filter_tasks(completed=False)

    if incomplete_tasks:
        task_to_complete = st.selectbox(
            "Select a task to mark complete:",
            options=range(len(incomplete_tasks)),
            format_func=lambda i: f"{incomplete_tasks[i].name} ({incomplete_tasks[i].duration} min)"
        )

        if st.button("Mark as Complete"):
            selected_task = incomplete_tasks[task_to_complete]

            # Use the scheduler's complete_task method
            new_recurring_task = st.session_state.scheduler.complete_task(selected_task)

            if new_recurring_task:
                st.success(f"✅ Completed '{selected_task.name}'!")
                st.info(f"🔄 Recurring task detected! Created new task for {new_recurring_task.due_date.strftime('%Y-%m-%d') if new_recurring_task.due_date else 'next occurrence'}")
            else:
                st.success(f"✅ Completed '{selected_task.name}'!")

            st.rerun()
    else:
        st.success("🎉 All tasks completed!")
else:
    st.info("No tasks available. Add some tasks first.")

st.divider()

# ========== DELETE TASKS ==========
st.subheader("🗑️ Delete Tasks")

if st.session_state.scheduler.tasks:
    # Show all tasks (both completed and incomplete)
    all_tasks = st.session_state.scheduler.tasks

    if all_tasks:
        task_to_delete = st.selectbox(
            "Select a task to delete:",
            options=range(len(all_tasks)),
            format_func=lambda i: f"{all_tasks[i].name} ({all_tasks[i].duration} min) - {'✓ Complete' if all_tasks[i].completed else '○ Pending'}",
            key="delete_task_select"
        )

        if st.button("Delete Task", type="secondary"):
            selected_task = all_tasks[task_to_delete]
            task_name = selected_task.name

            # Remove from scheduler's task list
            if selected_task in st.session_state.scheduler.tasks:
                st.session_state.scheduler.tasks.remove(selected_task)

            # Remove from pet's task list
            if selected_task in st.session_state.pet.tasks:
                st.session_state.pet.tasks.remove(selected_task)

            # Remove from UI-friendly tasks list (find matching entry by name)
            st.session_state.tasks = [
                t for t in st.session_state.tasks
                if t.get("title") != task_name
            ]

            st.success(f"🗑️ Deleted '{task_name}'!")
            st.rerun()
    else:
        st.info("No tasks available to delete.")
else:
    st.info("No tasks available. Add some tasks first.")

st.divider()

# ========== EDIT TASKS ==========
st.subheader("✏️ Edit Tasks")

if st.session_state.scheduler.tasks:
    all_tasks = st.session_state.scheduler.tasks

    if all_tasks:
        # Select task to edit
        task_to_edit_idx = st.selectbox(
            "Select a task to edit:",
            options=range(len(all_tasks)),
            format_func=lambda i: f"{all_tasks[i].name} ({all_tasks[i].duration} min, Priority: {all_tasks[i].priority})",
            key="edit_task_select"
        )

        selected_task = all_tasks[task_to_edit_idx]

        # Create input fields pre-filled with current values
        st.markdown("**Update task details:**")

        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Task name", value=selected_task.name, key="edit_name")
        with col2:
            new_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=selected_task.duration, key="edit_duration")
        with col3:
            # Map current priority to string for display
            priority_reverse_map = {1: "low", 2: "medium", 3: "high"}
            current_priority_str = priority_reverse_map.get(selected_task.priority, "medium")
            priority_options = {"low": 1, "medium": 2, "high": 3}
            new_priority_str = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=["low", "medium", "high"].index(current_priority_str),
                key="edit_priority"
            )

        col4, col5 = st.columns(2)
        with col4:
            new_time = st.text_input(
                "Time of day (optional, e.g., 09:00)",
                value=selected_task.time if selected_task.time else "",
                placeholder="HH:MM",
                key="edit_time"
            )
        with col5:
            current_recurrence = selected_task.recurrence if selected_task.recurrence else "none"
            new_recurrence = st.selectbox(
                "Recurrence",
                ["none", "daily", "weekly"],
                index=["none", "daily", "weekly"].index(current_recurrence),
                key="edit_recurrence"
            )

        if st.button("Update Task", type="primary"):
            # Use the edit_task() method for name, duration, and priority
            selected_task.edit_task(
                name=new_name,
                duration=int(new_duration),
                priority=priority_options[new_priority_str]
            )

            # Update time and recurrence (not covered by edit_task method)
            selected_task.time = new_time if new_time else None
            selected_task.recurrence = new_recurrence

            # Recalculate due_date if time changed
            if new_time:
                try:
                    time_parts = new_time.split(":")
                    if len(time_parts) == 2:
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        selected_task.due_date = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                except (ValueError, IndexError):
                    st.warning("⚠️ Invalid time format. Use HH:MM (e.g., 09:00)")
            else:
                selected_task.due_date = None

            # Update UI-friendly tasks list
            for i, task_dict in enumerate(st.session_state.tasks):
                if task_dict.get("title") == all_tasks[task_to_edit_idx].name:
                    st.session_state.tasks[i] = {
                        "title": new_name,
                        "duration_minutes": int(new_duration),
                        "priority": new_priority_str
                    }
                    break

            st.success(f"✏️ Updated '{new_name}'!")
            st.rerun()
    else:
        st.info("No tasks available to edit.")
else:
    st.info("No tasks available. Add some tasks first.")

st.divider()

# ========== TASK ANALYSIS SECTION ==========
st.subheader("📊 Task Analysis")

if st.session_state.scheduler.tasks:
    col1, col2 = st.columns(2)

    with col1:
        # Show chronological view using sort_by_time()
        st.markdown("**Chronological View**")
        sorted_tasks = st.session_state.scheduler.sort_by_time()
        if sorted_tasks:
            chron_data = []
            for task in sorted_tasks:
                chron_data.append({
                    "Time": task.time if task.time else "⚠ Unscheduled",
                    "Task": task.name,
                    "Duration": f"{task.duration} min"
                })
            st.table(chron_data)
        else:
            st.info("Add time information to tasks for chronological sorting")

    with col2:
        # Check for conflicts using detect_conflicts()
        st.markdown("**Conflict Detection**")
        conflicts = st.session_state.scheduler.detect_conflicts()

        if conflicts:
            st.warning(f"⚠️ Found {len(conflicts)} conflict(s)!")
            for i, (task1, task2) in enumerate(conflicts, 1):
                with st.container():
                    st.error(f"**Conflict {i}:**")
                    st.text(f"• {task1.name} ({task1.duration} min)")
                    st.text(f"• {task2.name} ({task2.duration} min)")
                    if task1.due_date and task2.due_date:
                        st.caption(f"Overlap: {task1.due_date.strftime('%Y-%m-%d %H:%M')} - {task2.due_date.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.success("✓ No scheduling conflicts detected!")
            st.caption("All tasks have compatible time slots")

st.divider()

st.subheader("Build Schedule")
st.caption("Click to generate a schedule based on priority and available time.")

if st.button("Generate schedule"):
    if len(st.session_state.scheduler.tasks) == 0:
        st.warning("⚠️ No tasks to schedule. Add some tasks first!")
    else:
        # Check for conflicts BEFORE generating the plan
        conflicts = st.session_state.scheduler.detect_conflicts()
        if conflicts:
            st.warning("⚠️ **Scheduling Conflicts Detected!**")
            for task1, task2 in conflicts:
                conflict_msg = f"**'{task1.name}'** and **'{task2.name}'** have overlapping times"
                if task1.due_date and task2.due_date:
                    conflict_msg += f" (starting at {task1.due_date.strftime('%H:%M')} and {task2.due_date.strftime('%H:%M')})"
                st.warning(conflict_msg)
            st.divider()

        # Use the generate_plan() method from Scheduler class
        plan = st.session_state.scheduler.generate_plan()

        # Use the explain_plan() method to get the explanation
        explanation = st.session_state.scheduler.explain_plan()

        st.success(f"✅ Schedule generated for {st.session_state.pet.name}!")

        # Display the plan
        st.markdown("### 📋 Generated Schedule")
        if plan:
            # Sort the plan by time if tasks have time information
            scheduler_copy = Scheduler(st.session_state.owner, st.session_state.pet, plan)
            sorted_plan = scheduler_copy.sort_by_time() if any(t.time for t in plan) else plan

            plan_data = []
            priority_map = {1: "Low ⬇", 2: "Medium ➡", 3: "High ⬆"}
            for idx, task in enumerate(sorted_plan, 1):
                plan_data.append({
                    "Order": idx,
                    "Task": task.name,
                    "Duration (min)": task.duration,
                    "Priority": priority_map.get(task.priority, str(task.priority)),
                    "Time": task.time if task.time else "Flexible",
                    "Status": "✓ Scheduled"
                })
            st.table(plan_data)

            # Show total time with color-coded progress
            total_time = sum(task.duration for task in plan)
            available_time = st.session_state.owner.preferences.get('available_time', 0)
            time_percentage = (total_time / available_time * 100) if available_time > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Time", f"{total_time} min")
            with col2:
                st.metric("Available Time", f"{available_time} min")
            with col3:
                st.metric("Time Used", f"{time_percentage:.1f}%")

            # Show color-coded message based on time usage
            if time_percentage > 90:
                st.warning(f"⚠️ Schedule is at {time_percentage:.1f}% capacity!")
            elif time_percentage > 70:
                st.info(f"⏱️ Schedule uses {time_percentage:.1f}% of available time")
            else:
                st.success(f"✓ Efficient schedule using {time_percentage:.1f}% of available time")

            # Show unscheduled tasks if any
            unscheduled = [t for t in st.session_state.scheduler.tasks if t not in plan]
            if unscheduled:
                st.warning(f"⚠️ **{len(unscheduled)} task(s) could not be scheduled** due to time constraints:")
                for task in unscheduled:
                    st.text(f"  • {task.name} ({task.duration} min)")
        else:
            st.warning("⚠️ No tasks could be scheduled. Try increasing available time.")

        # Display the explanation
        st.markdown("### 💡 Scheduling Explanation")
        st.info(explanation)

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
