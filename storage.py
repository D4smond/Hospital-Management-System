"""Saving and loading everything to a single file between runs."""

import pickle

FILE = 'hms_data.pkl'


def save_data(admin, doctors, patients, discharged_patients, appointments):
    # the admin is saved too, otherwise a changed password was forgotten
    # the next time the program started
    data = {
        'version': 2,
        'admin': admin,
        'doctors': doctors,
        'patients': patients,
        'discharged_patients': discharged_patients,
        'appointments': appointments,
    }
    with open(FILE, 'wb') as f:
        pickle.dump(data, f)


def load_data():
    """Return (admin, doctors, patients, discharged_patients, appointments).

    admin is None for files saved by older versions. Raises
    FileNotFoundError if there's no save file yet.
    """
    with open(FILE, 'rb') as f:
        data = pickle.load(f)

    if isinstance(data, dict):
        return (data['admin'], data['doctors'], data['patients'],
                data['discharged_patients'], data['appointments'])

    # older saves were plain tuples of 3 or 4 items
    if len(data) == 3:
        doctors, patients, discharged_patients = data
        return None, doctors, patients, discharged_patients, []

    doctors, patients, discharged_patients, appointments = data
    return None, doctors, patients, discharged_patients, appointments
