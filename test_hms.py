"""Automated versions of my test cases.

Run with:  python -m unittest -v

input() is patched with a list of answers so each test types exactly what
a user would, and print output is captured so I can check the messages.
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import storage
from Admin import Admin
from Doctor import Doctor
from Patient import Patient


def run(func, answers, *args):
    """Call func with input() answering from `answers`, return (result, printed text)."""
    out = io.StringIO()
    with patch('builtins.input', side_effect=answers), redirect_stdout(out):
        result = func(*args)
    return result, out.getvalue()


class HMSTests(unittest.TestCase):

    def setUp(self):
        self.admin = Admin('admin', '123')
        self.doctors = [Doctor('John', 'Smith', 'Internal Med.'), Doctor('Jone', 'Carlos', 'Cardiology')]
        self.patients = [
            Patient('Sara', 'Smith', 20, '07012345678', 'B1 234', ['Chest pain']),
            Patient('Mike', 'Jones', 37, '07555551234', 'L2 2AB', ['Fever']),
        ]
        self.discharged = []
        self.appointments = []

    # TC1 / TC2
    def test_login(self):
        self.assertTrue(run(self.admin.login, ['admin', '123'])[0])
        self.assertFalse(run(self.admin.login, ['admin', 'wrong'])[0])

    def test_full_name_has_a_space(self):
        self.assertEqual(self.doctors[0].full_name(), 'John Smith')

    # TC3
    def test_register_doctor(self):
        run(self.admin.doctor_management, ['1', 'Ada', 'Okafor', 'Neurology'],
            self.doctors, self.patients, self.appointments)
        self.assertEqual(self.doctors[-1].full_name(), 'Ada Okafor')

    # TC5
    def test_duplicate_doctor_rejected(self):
        _, text = run(self.admin.doctor_management, ['1', 'john', 'SMITH', 'Surgery'],
                      self.doctors, self.patients, self.appointments)
        self.assertIn('already exists', text)
        self.assertEqual(len(self.doctors), 2)

    # TC6
    def test_update_speciality(self):
        run(self.admin.doctor_management, ['3', '1', '3', 'Oncology'],
            self.doctors, self.patients, self.appointments)
        self.assertEqual(self.doctors[0].get_speciality(), 'Oncology')

    def test_renaming_doctor_keeps_patient_link(self):
        self.patients[0].link('John Smith')
        run(self.admin.doctor_management, ['3', '1', '2', 'Doe'],
            self.doctors, self.patients, self.appointments)
        self.assertEqual(self.patients[0].get_doctor(), 'John Doe')

    def test_update_handles_letters_instead_of_numbers(self):
        # used to crash with ValueError
        _, text = run(self.admin.doctor_management, ['3', 'abc', ''],
                      self.doctors, self.patients, self.appointments)
        self.assertIn('Please enter a number', text)

    # TC7
    def test_delete_doctor_unlinks_patients(self):
        self.patients[0].link('John Smith')
        _, text = run(self.admin.doctor_management, ['4', '1'],
                      self.doctors, self.patients, self.appointments)
        self.assertEqual(len(self.doctors), 1)
        self.assertEqual(self.patients[0].get_doctor(), 'None')
        self.assertNotIn('incorrect', text)  # old version always printed an error here

    def test_delete_with_bad_id_does_not_crash(self):
        run(self.admin.doctor_management, ['4', '99'], self.doctors, self.patients, self.appointments)
        self.assertEqual(len(self.doctors), 2)

    # TC8
    def test_assign_doctor_logs_appointment(self):
        run(self.admin.assign_doctor_to_patient, ['2', '2'], self.patients, self.doctors, self.appointments)
        self.assertEqual(self.patients[1].get_doctor(), 'Jone Carlos')
        self.assertEqual(len(self.appointments), 1)

    # TC9
    def test_discharge(self):
        run(self.admin.discharge, ['1'], self.patients, self.discharged)
        self.assertEqual(len(self.patients), 1)
        self.assertEqual(self.discharged[0].full_name(), 'Sara Smith')

    # TC10
    def test_password_rules(self):
        _, text = run(self.admin.update_details, ['2', 'short', 'short'])
        self.assertIn('at least 8', text)
        _, text = run(self.admin.update_details, ['2', 'longenough1', 'different1'])
        self.assertIn('do not match', text)
        run(self.admin.update_details, ['2', 'longenough1', 'longenough1'])
        self.assertTrue(run(self.admin.login, ['admin', 'longenough1'])[0])

    def test_report_lists_every_doctor(self):
        # the old report only printed the last doctor
        self.appointments.append({'doctor': 'John Smith', 'month': '2026-01'})
        _, text = run(self.admin.appointment_report, [], self.doctors, self.patients, self.appointments)
        self.assertIn('John Smith:', text)
        self.assertIn('Jone Carlos: 0 appointments', text)

    def test_report_numbers(self):
        self.patients[0].link('John Smith')
        report = self.admin.build_report(self.doctors, self.patients, self.appointments)
        self.assertEqual(report['total_doctors'], 2)
        self.assertEqual(report['patients_per_doctor']['John Smith'], 1)
        self.assertEqual(report['illness_counts']['Fever'], 1)

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            original = storage.FILE
            storage.FILE = os.path.join(folder, 'test.pkl')
            try:
                storage.save_data(self.admin, self.doctors, self.patients, self.discharged, self.appointments)
                admin, doctors, patients, discharged, appointments = storage.load_data()
            finally:
                storage.FILE = original
        self.assertEqual([d.full_name() for d in doctors], ['John Smith', 'Jone Carlos'])
        self.assertTrue(run(admin.login, ['admin', '123'])[0])


if __name__ == '__main__':
    unittest.main()
