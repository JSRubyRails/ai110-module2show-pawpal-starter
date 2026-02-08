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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
