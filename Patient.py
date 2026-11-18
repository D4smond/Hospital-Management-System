class Patient:
    """A patient in the hospital system."""

    def __init__(self, first_name, surname, age, mobile, postcode, symptoms=None):
        """
        Args:
            first_name (str): First name
            surname (str): Surname
            age (int): Age
            mobile (str): Mobile number (kept as a string so the leading 0 isn't lost)
            postcode (str): Postcode
            symptoms (list[str], optional): Symptoms the patient came in with
        """
        self.__first_name = first_name
        self.__surname = surname
        self.__age = age
        self.__mobile = mobile
        self.__postcode = postcode
        self.__symptoms = list(symptoms) if symptoms else []
        self.__doctor = 'None'  # string rather than None so it prints straight into the table

    def full_name(self):
        return f'{self.__first_name} {self.__surname}'

    def get_doctor(self):
        return self.__doctor

    def link(self, doctor):
        """Assign this patient to a doctor.

        Args:
            doctor (str): the doctor's full name
        """
        self.__doctor = doctor

    def unlink(self):
        """Used when the patient's doctor is deleted from the system."""
        self.__doctor = 'None'

    def get_symptoms(self):
        # return a copy so nothing outside the class can edit the list directly
        return list(self.__symptoms)

    def add_symptom(self, symptom):
        if symptom and symptom not in self.__symptoms:
            self.__symptoms.append(symptom)

    def print_symptoms(self):
        if not self.__symptoms:
            print('  (no symptoms recorded)')
        for symptom in self.__symptoms:
            print('  - ' + symptom)

    def __str__(self):
        return f'{self.full_name():^30}|{self.__doctor:^30}|{self.__age:^5}|{self.__mobile:^15}|{self.__postcode:^10}'
