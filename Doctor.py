class Doctor:
    """A doctor in the hospital system."""

    def __init__(self, first_name, surname, speciality):
        """
        Args:
            first_name (str): First name
            surname (str): Surname
            speciality (str): What the doctor specialises in, e.g. Cardiology
        """
        self.__first_name = first_name
        self.__surname = surname
        self.__speciality = speciality

    def full_name(self):
        # was missing the space before, so everyone came out as "JohnSmith"
        return f'{self.__first_name} {self.__surname}'

    def get_first_name(self):
        return self.__first_name

    def set_first_name(self, new_first_name):
        self.__first_name = new_first_name

    def get_surname(self):
        return self.__surname

    def set_surname(self, new_surname):
        self.__surname = new_surname

    def get_speciality(self):
        return self.__speciality

    def set_speciality(self, new_speciality):
        self.__speciality = new_speciality

    def __str__(self):
        # fixed-width columns so the doctor list lines up as a table
        return f'{self.full_name():^30}|{self.__speciality:^15}'
