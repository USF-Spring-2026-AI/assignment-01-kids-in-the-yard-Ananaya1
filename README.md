Comparison with LLM Assistance

Q1. Which tool did you use?

I used Cursor as my primary LLM-assisted development environment because it integrates code generation with structured Python editing and supports iterative refinement of object-oriented designs.

Q2. Prompt Used

You are helping me review an OO Python implementation for a family tree simulator.

Requirements:
- Two initial people born in 1950.
- For each person, year died = life_expectancy for birth decade +/- 10.
- Partner/spouse: at most 1 partner; probability = marriage_rate for their birth decade; spouse birth year within +/-10 years.
- Children count: based on birth_rate for birth decade +/- 1.5, rounding UP (ceiling). (CS 562 extension: if no spouse, 1 fewer child.)
- Children’s birth years must be evenly distributed between elder parent’s birth year +25 and +45.
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
Q3. Key Differences Between My Implementation and the LLM
The Cursor-generated design emphasized a more generalized simulation pattern and introduced additional abstraction layers that were not necessary for this assignment. In contrast, my implementation follows a generation-driven approach that more directly matches the assignment requirement of expanding the family tree until the year 2120.
My implementation also makes explicit design choices that closely follow the specification, such as evenly spacing children’s birth years within the elder parent’s +25 to +45 window and consistently using the elder parent’s birth decade when computing birth-related values where interpretation was required. While the LLM suggested multiple possible interpretations, I selected the approach that best aligns with the assignment wording.
Additionally, my code keeps the probabilistic logic more explicit and traceable, whereas the LLM design tended to hide some details behind additional abstraction layers.

Q4. Changes I Would Make

Based on the LLM suggestions, I would improve the modularity of my FamilyTree driver logic by separating major steps—such as spouse creation, child generation, and stopping conditions—into clearer helper methods. This would improve readability and maintainability.
I would also make the simulation more testable by injecting a fixed random seed (or passing a random.Random instance into the factory). This ensures reproducible results, which is helpful for debugging and for writing reliable unit tests.

Q5. Changes I Would Refuse

I would refuse changes that reduce transparency or correctness of the assignment’s required logic, even if they make the code shorter.
For example, I would not switch to Pandas solely to load CSV files, since it introduces an unnecessary dependency and can obscure the underlying logic. The built-in csv module is sufficient and clearer for this project.
I would also refuse any change that violates the specification—such as replacing the required ceiling (round up) rule for child counts with round() or truncation, or changing the “evenly distributed” child birth-year requirement into a different interpretation.
More generally, I would avoid abstraction that makes it harder to verify when marriage and birth probabilities are applied or whether the simulation output matches the assignment requirements.
