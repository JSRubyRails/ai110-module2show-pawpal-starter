import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Plan

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

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Keep a single Pet object alive across reruns; rebuild it if the inputs change.
if "pet" not in st.session_state or st.session_state.pet.name != pet_name:
    owner = Owner(name=owner_name)
    pet = Pet(name=pet_name, species=species)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet

pet: Pet = st.session_state.pet

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(Task(title=task_title, duration_minutes=int(duration), priority=priority))

if pet.list_tasks():
    st.write("Current tasks (sorted by priority):")
    # Preview the order the scheduler will consider tasks in: high priority
    # first, shorter tasks breaking ties. Uses the same Scheduler logic as
    # the real plan so the display matches what gets scheduled. Sorting is
    # independent of the time budget, so the value here is just a placeholder.
    preview = Scheduler(available_minutes=1440).sort_by_priority(pet.list_tasks())
    st.table(
        [
            {"title": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority}
            for t in preview
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=1440, value=120
)

if st.button("Generate schedule"):
    if not pet.list_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(available_minutes=int(available_minutes))
        plan: Plan = scheduler.build_plan(pet.list_tasks(), pet_name=pet.name)

        # Order the slots chronologically before display/conflict checks so the
        # table reads top-to-bottom by start time.
        plan.entries = scheduler.sort_by_time(plan.entries)

        st.markdown(f"### Today's Schedule for {pet.name}")
        if plan.entries:
            st.success(
                f"Scheduled {len(plan.entries)} task(s) using "
                f"{plan.total_minutes} of {int(available_minutes)} available minutes."
            )
            st.table(plan.to_table())
        else:
            st.warning("No tasks could be scheduled within the available time.")

        # Surface any overlapping time slots using the Scheduler's own
        # conflict detection.
        conflicts = scheduler.detect_conflicts(plan.entries)
        for warning in conflicts:
            st.warning(warning)

        st.markdown("**Why this plan?**")
        st.text(plan.explain())

        if plan.skipped:
            st.warning(
                "Skipped (not enough time): "
                + ", ".join(t.title for t in plan.skipped)
            )
