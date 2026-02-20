"""
PersonFactory: Generates realistic Person objects with names, birth/death years,
and family relationships based on historical demographic data.
"""
import csv
import random
from person import Person


class PersonFactory:
    """
    Factory class for creating Person objects with realistic demographic attributes.
    Uses CSV data files to generate names, life expectancy, and family relationships
    based on historical trends by decade.
    """
    def __init__(self):
        # Life expectancy by decade (e.g., 1980 → 74.5)
        self.life_exp_by_decade = {}

        # Birth + marriage rates by decade
        self.rates_by_decade = {}

        # First name data keyed by (decade, gender)
        # Format: {(decade, gender): ([names], [weights])}
        self.first_names = {}

        # List of tuples: (last_name, rank)
        self.last_names = []

        # Mapping: rank → probability (for weighted last name selection)
        self.rank_prob = {}

        # Prepared lists for fast sampling
        self.last_name_choices = []
        self.last_name_weights = None  # None = uniform random

    # ---------- READ FILES ----------
    def read_files(self):
        """Load all CSV data into memory."""
        print("Reading CSV files...")
        self.life_exp_by_decade = self.read_life_expectancy("life_expectancy.csv")
        self.first_names = self.read_firstnames("first_names.csv")
        self.last_names = self.read_lastnames("last_names.csv")
        self.rank_prob = self.read_rank_probabilities("rank_to_probability.csv")
        self.rates_by_decade = self.read_birth_marriage_rates("birth_and_marriage_rates.csv")

        # Prepare weighted distribution for last names
        self.prepare_last_name_distribution()

    def parse_decade(self, text):
        """Convert strings like '1980s' → 1980."""
        return int(str(text).replace("s", "").strip())

    def get_decade(self, year):
        """Return the decade of a year (e.g., 1987 → 1980)."""
        return (year // 10) * 10

    def read_life_expectancy(self, filename):
        """
        Read life expectancy CSV.
        Expected format: decade, life_expectancy
        Returns dict mapping decade (int) → life expectancy (float).
        """
        data = {}
        with open(filename) as file:
            reader = csv.reader(file)
            first = True
            for row in reader:
                if not row:
                    continue

                # Skip header row if present (check if first column is not a decade)
                if first:
                    first = False
                    try:
                        _ = self.parse_decade(row[0])
                    except:
                        # If parsing fails, this is likely a header row
                        continue

                decade = self.parse_decade(row[0])
                life_exp = float(row[1])
                data[decade] = life_exp
        return data

    def read_firstnames(self, filename):
        """
        Read first name frequencies by decade and gender.
        Expected format: decade, gender, name, frequency
        Returns dict mapping (decade, gender) → ([names], [weights]).
        """
        data = {}
        with open(filename) as file:
            reader = csv.reader(file)
            first = True
            for row in reader:
                if not row:
                    continue

                # Skip header if present
                if first:
                    first = False
                    if str(row[0]).lower().strip() in ["decade", "decades"]:
                        continue

                decade = self.parse_decade(row[0])

                # Normalize gender to "M" or "F" format
                gender_raw = str(row[1]).strip().lower()
                if gender_raw == "female":
                    gender = "F"
                elif gender_raw == "male":
                    gender = "M"
                else:
                    # Keep original format if not standard
                    gender = str(row[1]).strip()

                name = str(row[2]).strip()
                freq = float(row[3])

                key = (decade, gender)

                # Store names and weights separately for weighted random selection
                if key not in data:
                    data[key] = ([], [])
                names, weights = data[key]
                names.append(name)
                weights.append(freq)

        return data

    def read_lastnames(self, filename):
        """
        Read last names and their ranks from CSV.
        Handles multiple CSV formats: DictReader with "name"/"rank" or "last_name"/"rank",
        or fallback parsing for non-standard formats.
        Returns list of tuples: [(last_name, rank), ...]
        """
        data = []
        with open(filename) as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row:
                    continue

                # Handle standard column names: "name" and "rank"
                if "name" in row and "rank" in row:
                    name = str(row["name"]).strip()
                    rank = int(str(row["rank"]).strip())
                    data.append((name, rank))
                    continue

                # Handle alternative column names: "last_name" and "rank"
                if "last_name" in row and "rank" in row:
                    name = str(row["last_name"]).strip()
                    rank = int(str(row["rank"]).strip())
                    data.append((name, rank))
                    continue

                # Fallback parsing if format is non-standard
                # Extract all values and try to identify rank and name
                values = [str(v).strip() for v in row.values()]

                rank = None
                name = None

                # Find rank (first integer value found)
                for v in values:
                    try:
                        rank = int(v)
                        break
                    except:
                        pass

                # Find name (first non-empty, non-numeric value)
                for v in values:
                    # Skip decade strings like "1980s"
                    if v.endswith("s") and v[:-1].isdigit():
                        continue
                    # Skip numeric values
                    if v.isdigit():
                        continue
                    # Use first non-empty string as name
                    if v != "":
                        name = v
                        break

                # Only add if both name and rank were found
                if name is not None and rank is not None:
                    data.append((name, rank))

        return data

    def read_rank_probabilities(self, filename):
        """
        Read mapping from rank → probability.
        Handles CSV files where rank and probability columns may be in either order.
        Also handles percentage format (e.g., "5.2%" → 5.2).
        Returns dict mapping rank (int) → probability (float).
        """
        data = {}
        with open(filename) as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or len(row) < 2:
                    continue

                # Try normal order: rank first, probability second
                try:
                    rank = int(str(row[0]).strip())
                    prob_str = str(row[1]).strip().replace("%", "")
                    prob = float(prob_str)
                    data[rank] = prob
                    continue
                except:
                    pass

                # Try swapped order: probability first, rank second
                try:
                    prob_str = str(row[0]).strip().replace("%", "")
                    prob = float(prob_str)
                    rank = int(str(row[1]).strip())
                    data[rank] = prob
                    continue
                except:
                    pass

        return data

    def prepare_last_name_distribution(self):
        """
        Prepare weighted sampling lists for last names.
        Creates parallel lists of names and their probabilities for efficient
        weighted random selection. Falls back to uniform distribution if no
        probability data is available.
        """
        choices = []
        weights = []

        # Build lists of names and their corresponding probabilities
        for name, rank in self.last_names:
            if rank in self.rank_prob:
                choices.append(name)
                weights.append(self.rank_prob[rank])

        # If no weights available → uniform fallback
        if len(weights) == 0:
            self.last_name_choices = [name for (name, rank) in self.last_names]
            self.last_name_weights = None
            return

        # Check if all weights are zero (invalid distribution)
        total = sum(weights)
        if total == 0:
            self.last_name_choices = [name for (name, rank) in self.last_names]
            self.last_name_weights = None
            return

        # Normalize weights to sum to 1.0 for proper probability distribution
        weights = [w / total for w in weights]
        self.last_name_choices = choices
        self.last_name_weights = weights

    def read_birth_marriage_rates(self, filename):
        """
        Read birth and marriage rates by decade.
        Expected format: decade, birth_rate, marriage_rate
        Returns dict mapping decade (int) → (birth_rate, marriage_rate) tuple.
        """
        data = {}
        with open(filename) as file:
            reader = csv.reader(file)
            first = True
            for row in reader:
                if not row:
                    continue

                # Skip header row if present
                if first:
                    first = False
                    if str(row[0]).lower().strip() in ["decade", "decades"]:
                        continue

                decade = self.parse_decade(row[0])
                birth_rate = float(row[1])
                marriage_rate = float(row[2])
                data[decade] = (birth_rate, marriage_rate)
        return data

    # ---------- PERSON GENERATION ----------
    def create_person(self, year_born):
        """
        Create a Person object with random attributes based on birth year.
        Generates random gender, first name, last name, and death year.
        Returns a Person instance.
        """
        gender = self.random_gender()
        first_name = self.generate_first_name(year_born, gender)
        last_name = self.generate_last_name()
        death_year = self.generate_year_died(year_born)
        return Person(first_name, last_name, year_born, death_year, gender)

    def random_gender(self):
        """Randomly return 'M' or 'F'."""
        return random.choice(["M", "F"])

    def generate_year_died(self, year_born):
        """
        Estimate death year using life expectancy + randomness.
        Uses life expectancy for the person's birth decade, plus random
        variation of ±10 years to simulate natural variation.
        """
        decade = self.get_decade(year_born)
        life_exp = self.life_exp_by_decade[decade]
        # Add random variation: ±10 years around the life expectancy
        return year_born + int(life_exp + random.randint(-10, 10))

    def has_partner(self, person):
        """
        Determine probabilistically if person has a partner.
        Uses marriage rate for the person's birth decade to decide.
        Returns True if random value is below the marriage rate threshold.
        """
        decade = self.get_decade(person.birth_year)
        birth_rate, marriage_rate = self.rates_by_decade[decade]
        return random.random() < marriage_rate

    def generate_first_name(self, year_born, gender):
        """
        Generate weighted random first name based on birth year and gender.
        Uses frequency-weighted selection from names popular in that decade.
        Falls back to any available gender for the decade if exact match not found.
        """
        decade = self.get_decade(year_born)
        key = (decade, gender)

        # Fallback if exact gender missing: use any available gender for that decade
        if key not in self.first_names:
            possible = [k for k in self.first_names.keys() if k[0] == decade]
            if not possible:
                raise ValueError("No first names available for decade " + str(decade))
            key = random.choice(possible)

        # Use weighted random selection based on name frequencies
        names, weights = self.first_names[key]
        return random.choices(names, weights=weights, k=1)[0]

    def generate_last_name(self):
        """
        Generate last name using weighted distribution.
        Uses probability-weighted selection if weights are available,
        otherwise falls back to uniform random selection.
        """
        if self.last_name_weights is None:
            # Uniform random selection (all names equally likely)
            return random.choice(self.last_name_choices)
        # Weighted random selection based on rank probabilities
        return random.choices(self.last_name_choices, weights=self.last_name_weights, k=1)[0]

    def create_partner(self, person):
        """
        Create a partner for the given person.
        Partner's birth year is within ±10 years of the person's birth year.
        Ensures minimum birth year of 1950 (data availability constraint).
        Establishes bidirectional partner relationship.
        """
        # Partner born within ±10 years of person
        year = person.birth_year + random.randint(-10, 10)
        # Ensure minimum year (data constraint)
        if year < 1950:
            year = 1950

        partner = self.create_person(year)
        # Establish bidirectional relationship
        person.add_partner(partner)
        partner.add_partner(person)
        return partner

    def number_of_children(self, person):
        """
        Estimate number of children based on birth rate for person's decade.
        Uses birth rate ±1.5 as the range for random selection.
        Returns integer between 0 and (birth_rate + 1.5).
        """
        decade = self.get_decade(person.birth_year)
        birth_rate, marriage_rate = self.rates_by_decade[decade]

        # Create range around birth rate (±1.5 children)
        low = round(birth_rate - 1.5)
        high = round(birth_rate + 1.5)
        # Ensure non-negative minimum
        if low < 0:
            low = 0

        return random.randint(low, high)

    def create_person_with_family_name(self, year_born, last1, last2):
        """
        Create a child person choosing last name from either parent.
        Randomly selects one of the two parent last names.
        Generates random gender and appropriate first name.
        """
        gender = self.random_gender()
        first = self.generate_first_name(year_born, gender)
        # Randomly inherit last name from either parent
        last = random.choice([last1, last2])
        died = self.generate_year_died(year_born)
        return Person(first, last, year_born, died, gender)

    def create_children(self, parent1, parent2, end_year=2120):
        """
        Generate children for a couple, spaced between ages 25–45 of elder parent.
        Children are evenly spaced across the fertility window with small random jitter.
        Skips children that would be born after end_year.
        Establishes parent-child relationships bidirectionally.
        """
        kids = []
        count = self.number_of_children(parent1)

        if count <= 0:
            return kids

        # Elder parent = smaller birth year (determines fertility window)
        elder_birth = min(parent1.birth_year, parent2.birth_year)
        # Typical fertility window: ages 25-45
        start = elder_birth + 25
        end = elder_birth + 45

        years = []

        # Generate evenly spaced birth years across the fertility window
        if count == 1:
            # Single child: random year in window
            years = [random.randint(start, end)]
        else:
            # Multiple children: evenly spaced with small random jitter
            step = (end - start) / (count - 1)
            for i in range(count):
                y = start + step * i
                # Add small random jitter (±1 year) for realism
                y = int(round(y + random.uniform(-1, 1)))

                # Clamp to valid range
                if y < start:
                    y = start
                if y > end:
                    y = end

                years.append(y)

        # Create child Person objects
        for year in years:
            # Skip if child would be born after cutoff year
            if year > end_year:
                continue

            # Create child with random gender and inherited last name
            child = self.create_person_with_family_name(
                year,
                parent1.last_name,
                parent2.last_name
            )

            # Establish bidirectional parent-child relationships
            parent1.add_child(child)
            parent2.add_child(child)
            kids.append(child)

        return kids


# ---------- TESTS ----------
def test_family(factory):
    """
    Test function to demonstrate family generation.
    Creates a person, potentially adds a partner, and generates children.
    """
    print("\n--- FAMILY TEST ---")
    person = factory.create_person(1980)
    print("Person:", person)

    # Check if person should have a partner (based on marriage rate)
    if factory.has_partner(person):
        partner = factory.create_partner(person)
        print("Partner:", partner)

        # Generate children for the couple (using default end_year of 2120)
        kids = factory.create_children(person, partner)

        print("Children:")
        for k in kids:
            print("  ", k)
    else:
        print("No partner this time, so no children.")


def run_tests():
    """
    Main test runner: initializes factory, loads data, and runs family test.
    """
    factory = PersonFactory()
    factory.read_files()
    test_family(factory)


if __name__ == "__main__":
    run_tests()