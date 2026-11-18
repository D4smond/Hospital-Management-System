from datetime import datetime
from collections import Counter, defaultdict

from Doctor import Doctor


def ask_int(prompt):
    """Keep asking until the user types a whole number.

    A lot of the old crashes were just int(input()) blowing up when someone
    typed a letter, so everything that needs a number goes through here.
    Returns None if they just press Enter, so they can back out.
    """
    while True:
        answer = input(prompt).strip()
        if answer == '':
            return None
        try:
            return int(answer)
        except ValueError:
            print('Please enter a number (or press Enter to cancel).')


class Admin:
    """Handles everything the admin can do in the system."""

    def __init__(self, username, password, address=''):
        """
        Args:
            username (str): Username
            password (str): Password
            address (str, optional): Address. Defaults to ''.
        """
        self.__username = username
        self.__password = password
        self.__address = address

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def view(self, a_list):
        """Print a numbered list. IDs shown to the user start at 1."""
        for index, item in enumerate(a_list):
            print(f'{index + 1:3}|{item}')

    def pick_from(self, items, prompt):
        """Ask for an ID and return the matching list index, or None.

        Handles the "minus one" conversion in one place, plus bad input and
        IDs that don't exist.
        """
        if not items:
            print('There is nothing to choose from.')
            return None
        choice = ask_int(prompt)
        if choice is None:
            return None
        if 1 <= choice <= len(items):
            return choice - 1
        print('No record with that ID.')
        return None

    def login(self):
        """Ask for username and password, return True if they match."""
        print('-----Login-----')
        username = input('Enter the username: ')
        password = input('Enter the password: ')
        return username == self.__username and password == self.__password

    # ------------------------------------------------------------------
    # doctors
    # ------------------------------------------------------------------

    def get_doctor_details(self):
        """Ask for the details needed to register a doctor."""
        first_name = input('Enter the first name: ').strip()
        surname = input('Enter the surname: ').strip()
        speciality = input('Enter the speciality: ').strip()
        return first_name, surname, speciality

    def doctor_management(self, doctors, patients, appointments):
        """Register, view, update or delete doctors.

        patients and appointments are passed in as well because they refer
        to doctors by name, so renaming or deleting a doctor has to update
        them too, otherwise patients end up linked to a doctor that no
        longer exists.
        """
        print('-----Doctor Management-----')
        print('Choose the operation:')
        print(' 1 - Register')
        print(' 2 - View')
        print(' 3 - Update')
        print(' 4 - Delete')
        op = input('Input: ').strip()

        if op == '1':
            self.register_doctor(doctors)
        elif op == '2':
            print('-----List of Doctors-----')
            print('ID |          Full name           |  Speciality')
            self.view(doctors)
        elif op == '3':
            self.update_doctor(doctors, patients, appointments)
        elif op == '4':
            self.delete_doctor(doctors, patients)
        else:
            print('Invalid operation chosen. Check your spelling!')

    def register_doctor(self, doctors):
        print('-----Register-----')
        print("Enter the doctor's details:")
        first_name, surname, speciality = self.get_doctor_details()

        if not first_name or not surname:
            print('First name and surname are both needed.')
            return

        # case-insensitive so "john smith" and "John Smith" count as the same person
        for doctor in doctors:
            if (first_name.lower() == doctor.get_first_name().lower()
                    and surname.lower() == doctor.get_surname().lower()):
                print('Name already exists.')
                return

        doctors.append(Doctor(first_name, surname, speciality))
        print('Doctor registered.')

    def update_doctor(self, doctors, patients, appointments):
        print("-----Update Doctor's Details-----")
        print('ID |          Full name           |  Speciality')
        self.view(doctors)
        index = self.pick_from(doctors, 'Enter the ID of the doctor: ')
        if index is None:
            return

        doctor = doctors[index]
        old_name = doctor.full_name()

        print('Choose the field to be updated:')
        print(' 1 First name')
        print(' 2 Surname')
        print(' 3 Speciality')
        op = ask_int('Input: ')

        if op == 1:
            doctor.set_first_name(input('Enter the new first name: ').strip())
        elif op == 2:
            doctor.set_surname(input('Enter the new surname: ').strip())
        elif op == 3:
            doctor.set_speciality(input('Enter the new speciality: ').strip())
            print('Doctor updated.')
            return
        else:
            print('Wrong option.')
            return

        # name changed, so carry it across to their patients and appointment history
        new_name = doctor.full_name()
        for patient in patients:
            if patient.get_doctor() == old_name:
                patient.link(new_name)
        for appointment in appointments:
            if appointment.get('doctor') == old_name:
                appointment['doctor'] = new_name
        print('Doctor updated.')

    def delete_doctor(self, doctors, patients):
        print('-----Delete Doctor-----')
        print('ID |          Full Name           |  Speciality')
        self.view(doctors)
        index = self.pick_from(doctors, 'Enter the ID of the doctor to be deleted: ')
        if index is None:
            return

        removed = doctors.pop(index)
        # their patients now have nobody, so they need reassigning
        orphaned = 0
        for patient in patients:
            if patient.get_doctor() == removed.full_name():
                patient.unlink()
                orphaned += 1

        print(f'{removed.full_name()} deleted.')
        if orphaned:
            print(f'{orphaned} patient(s) no longer have a doctor and need reassigning.')

    # ------------------------------------------------------------------
    # patients
    # ------------------------------------------------------------------

    def view_patient(self, patients):
        print('-----View Patients-----')
        print('ID |          Full Name           |      Doctor`s Full Name      | Age |    Mobile     | Postcode ')
        if not patients:
            print('No active patients.')
        else:
            self.view(patients)

    def assign_doctor_to_patient(self, patients, doctors, appointments):
        """Link a patient to a doctor and log it as an appointment for this month."""
        print('-----Assign-----')
        self.view_patient(patients)
        patient_index = self.pick_from(patients, 'Please enter the patient ID: ')
        if patient_index is None:
            return
        patient = patients[patient_index]

        print('-----Doctors Select-----')
        print('Select the doctor that fits these symptoms:')
        patient.print_symptoms()
        print('--------------------------------------------------')
        print('ID |          Full Name           |  Speciality   ')
        self.view(doctors)
        doctor_index = self.pick_from(doctors, 'Please enter the doctor ID: ')
        if doctor_index is None:
            return
        doctor = doctors[doctor_index]

        previous = patient.get_doctor()
        patient.link(doctor.full_name())
        appointments.append({
            'doctor': doctor.full_name(),
            'month': datetime.now().strftime('%Y-%m'),
        })

        if previous not in ('None', doctor.full_name()):
            print(f'Patient moved from {previous} to {doctor.full_name()}.')
        else:
            print('The patient is now assigned to the doctor.')

    def discharge(self, patients, discharged_patients):
        """Move one patient from the active list to the discharged list.

        Returns True if someone was discharged.
        """
        print('-----Discharge Patient-----')
        self.view_patient(patients)
        index = self.pick_from(patients, 'Please enter the patient ID to discharge: ')
        if index is None:
            return False

        patient = patients.pop(index)
        discharged_patients.append(patient)
        print(f'{patient.full_name()} has been discharged.')
        return True

    def view_discharge(self, discharged_patients):
        print('-----Discharged Patients-----')
        print('ID |          Full Name           |      Doctor`s Full Name      | Age |    Mobile     | Postcode ')
        if not discharged_patients:
            print('No discharged patients.')
        else:
            self.view(discharged_patients)

    # ------------------------------------------------------------------
    # reports
    # ------------------------------------------------------------------

    def build_report(self, doctors, patients, appointments):
        """Work out all the report numbers in one place.

        Both the text report and the charts use this, so they can never
        disagree with each other.
        """
        patients_per_doctor = Counter(
            p.get_doctor() for p in patients if p.get_doctor() != 'None'
        )

        appointments_per_month = defaultdict(Counter)
        for appointment in appointments:
            if 'doctor' in appointment and 'month' in appointment:
                appointments_per_month[appointment['doctor']][appointment['month']] += 1

        # first recorded symptom is used as the illness type
        illness_counts = Counter(
            p.get_symptoms()[0] for p in patients if p.get_symptoms()
        )

        return {
            'total_doctors': len(doctors),
            'patients_per_doctor': patients_per_doctor,
            'appointments_per_month': appointments_per_month,
            'illness_counts': illness_counts,
        }

    def appointment_report(self, doctors, patients, appointments):
        """Print the management report."""
        report = self.build_report(doctors, patients, appointments)

        print('\n========== Management Report ==========')
        print(f"Total doctors in the system: {report['total_doctors']}")

        print('\n--- Patients per doctor ---')
        for doctor in doctors:
            name = doctor.full_name()
            print(f"- {name}: {report['patients_per_doctor'].get(name, 0)}")

        print('\n--- Appointments per month per doctor ---')
        # this block used to sit outside the loop, so only the last doctor got printed
        for doctor in doctors:
            name = doctor.full_name()
            months = report['appointments_per_month'].get(name)
            if not months:
                print(f'- {name}: 0 appointments')
                continue
            print(f'- {name}:')
            for month in sorted(months):
                print(f'    {month} -> {months[month]}')

        print('\n--- Patients by illness type ---')
        if not report['illness_counts']:
            print('No symptoms recorded yet.')
        for illness, count in report['illness_counts'].most_common():
            print(f'- {illness}: {count}')
        print('=======================================\n')

    def plot_diagrams(self, doctors, patients, appointments):
        """Show the four report charts in one window."""
        # imported here so the rest of the system still works on a machine
        # without matplotlib installed
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print('matplotlib is not installed. Run: pip install matplotlib')
            return

        report = self.build_report(doctors, patients, appointments)
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Hospital Management Report')

        # a) total doctors
        ax = axes[0][0]
        ax.bar(['Doctors'], [report['total_doctors']])
        ax.set_title('Total doctors')
        ax.set_ylabel('Count')

        # b) patients per doctor (show every doctor, including ones with 0)
        ax = axes[0][1]
        names = [d.full_name() for d in doctors]
        ax.bar(names, [report['patients_per_doctor'].get(n, 0) for n in names])
        ax.set_title('Patients per doctor')
        ax.tick_params(axis='x', rotation=25)

        # c) appointments per month, one set of bars per doctor
        ax = axes[1][0]
        per_doctor = report['appointments_per_month']
        if per_doctor:
            months = sorted({m for counts in per_doctor.values() for m in counts})
            width = 0.8 / len(per_doctor)
            for i, (name, counts) in enumerate(per_doctor.items()):
                positions = [x + i * width for x in range(len(months))]
                ax.bar(positions, [counts.get(m, 0) for m in months], width=width, label=name)
            ax.set_xticks([x + width * (len(per_doctor) - 1) / 2 for x in range(len(months))])
            ax.set_xticklabels(months)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'No appointments yet', ha='center', va='center')
        ax.set_title('Appointments per month per doctor')

        # d) patients by illness
        ax = axes[1][1]
        illness = report['illness_counts']
        if illness:
            ax.bar(list(illness.keys()), list(illness.values()))
            ax.tick_params(axis='x', rotation=25)
        else:
            ax.text(0.5, 0.5, 'No symptoms recorded', ha='center', va='center')
        ax.set_title('Patients by illness type')

        # counts are always whole numbers, no point showing 0.25, 0.5...
        from matplotlib.ticker import MaxNLocator
        for ax in axes.flat:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        fig.tight_layout()
        plt.show()

    # ------------------------------------------------------------------
    # admin's own details
    # ------------------------------------------------------------------

    def update_details(self):
        """Change the admin's username, password or address."""
        print('Choose the field to be updated:')
        print(' 1 Username')
        print(' 2 Password')
        print(' 3 Address')
        op = ask_int('Input: ')

        if op == 1:
            username = input('Enter the new username: ').strip()
            if not username:
                print('Username cannot be blank. No changes made.')
                return
            self.__username = username
            print('Username updated successfully.')

        elif op == 2:
            password = input('Enter the new password: ')
            confirm = input('Enter the new password again: ')
            if password != confirm:
                print('Passwords do not match. No changes made.')
            elif len(password) < 8:
                print('Password must be at least 8 characters. No changes made.')
            else:
                self.__password = password
                print('Password updated successfully.')

        elif op == 3:
            self.__address = input('Enter the new address: ').strip()
            print('Address updated successfully.')

        else:
            print('Wrong option.')
