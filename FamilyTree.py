"""
FamilyTree: Builds and manages a family tree using PersonFactory.
Generates family relationships across multiple generations within a time range.
"""
from collections import defaultdict, Counter


class FamilyTree:
    """
    Manages a family tree structure with query capabilities.
    Builds family relationships starting from an initial couple and expanding
    through generations up to a specified end year.
    """
    def __init__(self, factory, start_year=1950, end_year=2120):
        self.factory = factory
        self.start_year = start_year
        self.end_year = end_year
        self.roots = []   # Initial couple: [root1, root2]
        self.people = []  # All Person objects in the tree

    def create_initial_couple(self):
        """
        Create the initial couple for the family tree.
        Both people are born in 1950 (assignment requirement).
        Returns the two root Person objects.
        """
        y = 1950  # assignment requirement
        p1 = self.factory.create_person(y)
        p2 = self.factory.create_person(y)

        # Link them as partners (bidirectional relationship)
        p1.add_partner(p2)

        self.roots = [p1, p2]
        self.people = [p1, p2]
        return p1, p2

    def build(self):
        """
        Build the entire family tree using breadth-first traversal.
        Processes each person: creates partner if needed, then generates children.
        Continues until all eligible people have been processed up to end_year.
        """
        # Initialize roots if not already created
        if not self.roots:
            p1, p2 = self.create_initial_couple()
        else:
            p1, p2 = self.roots[0], self.roots[1]

        # Breadth-first queue: process people in order of birth
        queue = [p1, p2]

        while queue:
            person = queue.pop(0)
            partner = person.partner

            # Create partner probabilistically if none exists
            if partner is None and self.factory.has_partner(person):
                partner = self.factory.create_partner(person)
                self.people.append(partner)
                queue.append(partner)

            # Generate children only once per couple (process elder parent)
            # This prevents duplicate child generation
            if partner is not None and person.birth_year <= partner.birth_year:
                kids = self.factory.create_children(person, partner, self.end_year)
                for child in kids:
                    # Double-check end_year constraint (defensive programming)
                    if child.birth_year <= self.end_year:
                        self.people.append(child)
                        queue.append(child)

        return self.people

    # ----------------- QUERIES (menu) -----------------
    def total_people(self):
        """Return total number of people in the family tree."""
        return len(self.people)

    def total_people_by_decade(self):
        """
        Count people by birth decade.
        Returns dict mapping decade → count, sorted by decade.
        """
        counts = defaultdict(int)
        for p in self.people:
            decade = (p.birth_year // 10) * 10
            counts[decade] += 1
        return dict(sorted(counts.items()))

    def duplicate_full_names(self):
        """
        Find duplicate full names (first + last) in the tree.
        Returns dict mapping name → count, sorted by count (desc) then name (asc).
        """
        names = [p.get_full_name() for p in self.people]
        c = Counter(names)
        dups = {name: cnt for name, cnt in c.items() if cnt > 1}
        return dict(sorted(dups.items(), key=lambda x: (-x[1], x[0])))

    def run_cli(self):
        """
        Run interactive command-line interface for querying the family tree.
        Commands: T (total), D (by decade), N (duplicate names), Q (quit).
        """
        print("\nTree built.")
        print("Commands:")
        print("  T  -> total people")
        print("  D  -> total people by decade (birth decade)")
        print("  N  -> duplicate full names")
        print("  Q  -> quit\n")

        while True:
            cmd = input("Enter command (T/D/N/Q): ").strip().upper()

            if cmd == "Q":
                print("Bye!")
                break

            if cmd == "T":
                print("Total people:", self.total_people())
                continue

            if cmd == "D":
                counts = self.total_people_by_decade()
                for decade, cnt in counts.items():
                    print(f"{decade}s: {cnt}")
                continue

            if cmd == "N":
                dups = self.duplicate_full_names()
                if not dups:
                    print("No duplicate full names found.")
                else:
                    for name, cnt in dups.items():
                        print(f"{name}: {cnt}")
                continue

            print("Invalid command. Use T, D, N, or Q.")

    def summary(self):
        """Print a summary of the family tree statistics."""
        total = len(self.people)
        print("FamilyTree Summary")
        print("Start year:", self.start_year)
        print("End year:", self.end_year)
        print("Total people:", total)
        if self.roots:
            print("Roots:", self.roots[0], "AND", self.roots[1])


if __name__ == "__main__":
    from person_factory import PersonFactory

    factory = PersonFactory()
    factory.read_files()

    tree = FamilyTree(factory, start_year=1950, end_year=2120)
    tree.build()
    tree.summary()
    tree.run_cli()
