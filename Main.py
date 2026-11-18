"""Hospital Management System — run this file to start."""

import pickle

from Admin import Admin
from Doctor import Doctor
from Patient import Patient
from storage import save_data, load_data


def default_data():
    """Starting data for the very first run, before there's a save file."""
    admin = Admin('admin', '123', 'B1 1AB')
    doctors = [
        Doctor('John', 'Smith', 'Internal Med.'),
        Doctor('Jone', 'Smith', 'Pediatrics'),
        Doctor('Jone', 'Carlos', 'Cardiology'),
    ]
    patients = [
        Patient('Sara', 'Smith', 20, '07012345678', 'B1 234', ['Chest pain']),
        Patient('Mike', 'Jones', 37, '07555551234', 'L2 2AB', ['Fever', 'Cough']),
        Patient('David', 'Smith', 15, '07123456789', 'C1 ABC', ['Fever']),
    ]
    return admin, doctors, patients, [], []


def load_or_create():
    try:
        admin, doctors, patients, discharged, appointments = load_data()
        print('Loaded saved data.')
        if admin is None:  # save file from before admins were stored
            admin = Admin('admin', '123', 'B1 1AB')
        return admin, doctors, patients, discharged, appointments
    except FileNotFoundError:
        print('No save file yet, using default data.')
    except (pickle.UnpicklingError, EOFError, KeyError, ValueError):
        # don't crash if the file got corrupted, just start fresh
        print('Save file could not be read, starting with default data.')
    return default_data()


def print_menu():
    print('\nChoose the operation:')
    print(' 1 - Register/view/update/delete doctor')
    print(' 2 - View patients')
    print(' 3 - Discharge patients')
    print(' 4 - View discharged patients')
    print(' 5 - Assign doctor to a patient')
    print(' 6 - Update admin details')
    print(' 7 - Management report')
    print(' 8 - View report diagrams')
    print(' 9 - Save and quit')


def main():
    admin, doctors, patients, discharged_patients, appointments = load_or_create()

    # keep asking until the login is right
    while not admin.login():
        print('Incorrect username or password.')

    while True:
        print_menu()
        op = input('Option: ').strip()

        if op == '1':
            admin.doctor_management(doctors, patients, appointments)

        elif op == '2':
            admin.view_patient(patients)

        elif op == '3':
            # discharge one, then keep offering until they say no
            discharged_one = admin.discharge(patients, discharged_patients)
            while discharged_one and patients:
                again = input('Do you want to discharge another patient (Y/N): ').strip().lower()
                if again in ('y', 'yes'):
                    admin.discharge(patients, discharged_patients)
                elif again in ('n', 'no'):
                    break
                else:
                    print('Please answer by yes or no.')

        elif op == '4':
            admin.view_discharge(discharged_patients)

        elif op == '5':
            admin.assign_doctor_to_patient(patients, doctors, appointments)

        elif op == '6':
            admin.update_details()

        elif op == '7':
            admin.appointment_report(doctors, patients, appointments)

        elif op == '8':
            admin.plot_diagrams(doctors, patients, appointments)

        elif op == '9':
            save_data(admin, doctors, patients, discharged_patients, appointments)
            print('Saved data. Goodbye!')
            break

        else:
            print('Invalid option. Try again.')


if __name__ == '__main__':
    main()
