# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- The initial UML design should allow users to enter owner and pet information, generate a daily schedule that factors in constraints (time availability, etc.), and allow users to add or edit tasks (walking, feeding, etc.). I created four classes; owner, pet, task, and scheduler. The owner class represents the pet owner with attributes including name and preferences (scheduling constraints or task preferences), and methods handling update preferences or retrieving owner information. The pet class represents the pet with attributes including name, species, and age, with methods handling updating pet information or retrieving pet details. The task class represents a task set by the owner, with attributes including name of the task, duration, and priority, with methods handling editing task details or checking constraints. The scheduler class manages the scheduling logic, with attributes including references to the owner, pet, and task classes, and methods including generating a daily plan based on constraints and priorities. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Based on AI feedback I received, I didn't need to make any changes to my initial design since my description in 1a and the "skeletons" generated in pawpalsystem.py matches. The only minor implementation within the pawpalsystem.py is the use of dataclasses for the pet and task class to keep the code clean. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

- My scheduler considers several constraints:
- Available time: The owner's daily time budget (in minutes) limits which tasks can fit
- Task priority: Tasks are sorted by priority (higher numbers first) to ensure important tasks are scheduled
- Task duration: Each task's duration must fit within the remaining available time
- I decided that priority mattered most because pet care has critical tasks (like medication or feeding) that must happen regardless of other activities. Available time acts as a hard constraint - we can't schedule more than the owner has available. Duration is checked for each task to ensure feasibility.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- My scheduler makes a priority-first tradeoff: it always schedules higher-priority tasks before lower-priority ones, even if this leaves gaps in the schedule. For example, if I have 3 hours available and a high-priority 1-hour task, it schedules that first. If the remaining 2 hours can't fit the next high-priority task (which takes 3 hours), that task is skipped entirely - even if several lower-priority tasks could fit in those 2 hours.
- This tradeoff is reasonable for pet care because critical needs (medication, feeding) should always take precedence over optional activities (playtime, grooming). It's better to guarantee essential tasks happen than to optimize for filling every minute of the schedule. Pet owners would rather have their pet's urgent needs met with some free time left over than have a completely packed schedule that might skip important care.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used AI tools throughout the project for:
- Design brainstorming: I described my UML design and asked for feedback on the class structure and responsibilities
- Implementation: I used AI to help generate the class skeletons from my UML design and to implement methods like sort_by_time(), filter_tasks(), and detect_conflicts()
- Testing: I used AI to help create comprehensive test cases, including edge cases I hadn't thought of (like month/year boundaries for recurring tasks, boundary-touching conflicts)
- Debugging: When implementing recurring tasks with timedelta, I used AI to verify my date arithmetic logic

The most helpful prompts were specific and detailed, such as: "Implement a conflict detection method that checks if two tasks overlap based on their due_date and duration" or "Write pytest tests for the sort_by_time method including edge cases for None values and duplicate times."


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- One moment where I didn't accept an AI suggestion as-is was with the conflict detection logic. Initially, AI suggested using <= and >= operators for checking time overlaps, which would flag tasks as conflicting even if one ended exactly when another began (e.g., a task ending at 11:00 AM and another starting at 11:00 AM would conflict). 
- I evaluated this by thinking through real-world scenarios: if a walk ends at 11:00 AM, can feeding start immediately at 11:00 AM? In practice, yes - these activities can happen back-to-back without actual conflict. I verified this decision by writing a specific test case (test_conflict_detection_boundary_touching) to document the expected behavior, and adjusted the logic to use < and > operators instead. This ensures my system matches realistic pet care scheduling needs.


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- I tested several key behaviors:
- Sorting functionality: sort_by_time() with various inputs (empty lists, tasks with None times, duplicate times)
- Filtering: filter_tasks() by completion status and pet name
- Recurrence logic: Marking daily/weekly tasks complete to create new instances with correct due dates calculated using timedelta
- Conflict detection: Identifying overlapping tasks, handling edge cases like boundary touching and tasks on different days
- Basic operations: Task completion and adding tasks to pets

- These tests were important because:
- Sorting/filtering are core to usability - users need to view tasks in logical orders
- Recurrence logic involves complex date arithmetic that could easily have off-by-one errors
- Conflict detection prevents double-booking, which is critical for realistic scheduling
- Edge cases (month boundaries, year boundaries) catch bugs that only appear in specific scenarios


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?


- I'm fairly confident my scheduler works correctly for the implemented features due to the implementation of 28 successful tests that cover happy paths and edge cases, as well as the sorting, filtering, and conflict detection logic being able to handle different scenarios.

If I had more time, I would test:
- Leap year edge cases: Does a recurring task on Feb 29 work correctly in non-leap years?
- Multi-pet scenarios: How does scheduling work when managing tasks for multiple pets simultaneously with shared owner time?
- Complex recurrence patterns: What about bi-weekly tasks, or tasks that repeat on specific days of the week?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- I'm most satisfied with the clean separation of concerns in my design. Having distinct Owner, Pet, Task, and Scheduler classes made the code easy to understand and extend. When I needed to add new features like conflict detection or recurring tasks, I could add them to the appropriate class without restructuring everything.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- If I had another iteration, I would improve the scheduling algorithm to be smarter about filling available time. Currently, it uses a greedy priority-first approach that can leave gaps. I would implement a more sophisticated algorithm that considers multiple factors (priority, duration, time-of-day preferences) to maximize schedule utilization while still respecting priorities. I might also add a "must-do" flag for critical tasks to distinguish between high-priority and absolutely essential tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

- My key takeaway is that designing for testability from the start makes a huge difference. Because I separated concerns into clear classes with well-defined methods, writing tests was straightforward. I learned that thinking about "how will I verify this works?" while designing the system leads to better architecture than trying to add tests later. Good system design and good testing go hand-in-hand.
