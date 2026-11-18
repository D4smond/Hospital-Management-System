# Hospital Management System

A command-line hospital management system in Python, built for my first-year
Computer Programming module at Birmingham City University. An admin logs in
and manages doctors and patients, and everything is saved between runs.

## Running it

```
python Main.py
```

Default login is `admin` / `123` (you can change it from the menu, and the
new password is saved). The report diagrams need matplotlib:

```
pip install matplotlib
```

## What it does

- Register, view, update and delete doctors (duplicate names are rejected)
- View patients and assign them to a doctor, which also logs an appointment
  for the current month. Reassigning moves the patient to the new doctor
- Discharge patients and view the discharged list
- Update the admin's username, password (8+ characters, typed twice) and address
- Management report: total doctors, patients per doctor, appointments per
  month per doctor, and patients by illness type
- The same report as four charts in one matplotlib window
- Everything is saved to `hms_data.pkl` on quit and loaded on the next start

## How it's structured

```
Main.py      menu loop and start-up
Admin.py     everything the admin can do, plus the report and charts
Doctor.py    Doctor class
Patient.py   Patient class
storage.py   save/load with pickle (still reads saves from older versions)
test_hms.py  automated tests
```

All attributes are private (`self.__name`) with getters and setters, so
the only way to change a doctor or patient is through their methods.

## Tests

```
python -m unittest -v
```

15 tests. They cover my original 10 manual test cases (login, register,
duplicates, update, delete, assign, discharge, password rules) plus checks
for the bugs below. `input()` is patched with scripted answers, so each
test types exactly what a user would.

## Things I fixed after submitting

- The diagrams option only ever showed a leftover test plot because of an
  early `return`. It now draws all four charts.
- `full_name()` was missing a space, so names came out as "JohnSmith".
- The appointments report only printed the last doctor (indentation bug).
- The "View diagrams?" question was asked after every menu option and broke
  the menu, so some options also printed "Invalid option".
- Deleting a doctor always printed an error, and crashed on an ID that
  didn't exist. It now also unlinks that doctor's patients.
- Typing a letter where a number was expected crashed the program; every
  numeric prompt now re-asks instead.
- Renaming a doctor now carries the new name across to their patients and
  appointment history, since those are linked by name.
- A changed admin password is now saved instead of resetting to the
  default on the next run.
