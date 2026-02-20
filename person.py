class Person:
    """
    Represents a person with demographic information and family relationships.
    Tracks partner and children relationships for family tree construction.
    """

    def __init__(self, first_name, last_name, birth_year, death_year, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_year = birth_year
        self.death_year = death_year
        self.gender = gender

        # Family relationships
        self.partner = None
        self.children_list = []

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_age(self):
        """Calculate age at death. Returns None if person is still alive."""
        if self.death_year is not None:
            return self.death_year - self.birth_year
        else:
            return None   # still alive / unknown

    def get_partner(self):
        return self.partner

    def get_children(self):
        return self.children_list

    def add_child(self, child):
        self.children_list.append(child)

    def add_partner(self, partner):
        """Establish bidirectional partner relationship."""
        self.partner = partner
        partner.partner = self   # link both people

    def __str__(self):
        """String representation: "First Last (birth_year - death_year)"."""
        return self.get_full_name() + " (" + str(self.birth_year) + " - " + str(self.death_year) + ")"
