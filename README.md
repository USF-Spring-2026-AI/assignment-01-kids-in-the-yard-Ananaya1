# AI Assignment 01 - Kids in the Yard
Which tool did you use?
I used Cursor as my primary LLM-assisted development environment because it integrates code generation with structured Python editing and supports object-oriented design workflows.
Prompt:
    You are helping me review an OO Python implementation for a family tree simulator.

Requirements:
 - Two initial people born in 1950.
 - For each person, year died = life_expectancy for birth decade +/- 10.
  - Partner/spouse: at most 1 partner; probability = marriage_rate for their birth decade; spouse       birth year within +/-10 years.
  - Children count: based on birth_rate for birth decade +/- 1.5, rounding UP (ceiling). (CS 562   extension: if no spouse, 1 fewer child.)
- Children's birth years must be evenly distributed between older parents' birth years +25 and +45.
- First names from first_names.csv by decade+gender with probability proportional to frequency.
- Last names from last_names.csv using rank_to_probability.csv.
- After building tree until 2120, support interactive queries:
(T) total people, (D) total by decade/year, (N) duplicate full names.
- Clean style (PEP8), graceful failure.

Task:
1) Propose an OO design (Person, PersonFactory, FamilyTree) and key methods.
2) Identify common bugs/pitfalls with these requirements.
3) Suggest improvements to make the implementation more correct, readable, and testable.
4) Provide pseudocode (not full code) for the core algorithms.

Key Differences
The cursor code focused more on a generalized simulation pattern and added extra layers of abstraction which were not needed for the assignment. In contrast, my implementation focuses on a generation-driven approach that more directly matches the assignment requirements for building the family tree until 2120.
My implementation also makes explicit choices for evenly distributing child birth years and for determining child counts based on the elder parent’s birth decade. While the LLM suggested multiple possible interpretations, I selected the approach that most closely follows the assignment specification.





Changes
I would improve the modularity of my FamilyTree “driver” logic by separating steps like spouse creation, child generation, and stopping conditions into clearer helper methods. I would make the FamilyTree code easier to read and debug by splitting the big “build the whole tree” logic into a few small helper functions one that handles creating/linking a spouse (using the marriage probability once), one that handles generating/linking children (computing child count and evenly spaced birth years), and one that checks when to stop (no new births before 2120). Also using a fixed random seed (or a random.Random object) makes your results repeatable, so I get the same family tree every run, which is really helpful for debugging and for writing reliable tests.

Changes I refuse              										I would refuse changes that reduce transparency or correctness of the assignment’s required logic, even if they make the code shorter. For example, I would not switch to Pandas just to load CSVs if it hides what the program is doing or adds an unnecessary dependency, since simple csv parsing is clearer and fully sufficient for this project. I would also refuse any change that alters the required rounding rule for children or that replaces the “evenly distributed” child birth-year rule with a different interpretation. More generally, I would refuse extra abstraction that makes it harder to verify when marriage/birth probabilities are applied and whether the output matches the specification.

See assignment details on Canvas.
