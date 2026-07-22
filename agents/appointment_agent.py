from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PATIENT_DB = BASE_DIR / "database" / "patient_db.csv"
DOCTOR_SCHEDULE = BASE_DIR / "database" / "doctor_schedule.csv"
APPOINTMENTS = BASE_DIR / "database" / "appointments.csv"

DAY_NUMBERS = {
    "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3,
    "Fri": 4, "Sat": 5, "Sun": 6,
}


def _load_data():
    patients = pd.read_csv(PATIENT_DB, dtype=str).fillna("")
    doctors = pd.read_csv(DOCTOR_SCHEDULE, dtype=str).fillna("")
    appointments = pd.read_csv(APPOINTMENTS, dtype=str).fillna("")
    return patients, doctors, appointments


def _is_doctor_available_on_day(available_days: str, appointment_date: str) -> bool:
    day_number = datetime.strptime(appointment_date, "%Y-%m-%d").weekday()

    start_day, end_day = available_days.split("-")
    return DAY_NUMBERS[start_day] <= day_number <= DAY_NUMBERS[end_day]


def get_available_slots(doctor_id: str, appointment_date: str) -> list[str]:
    _, doctors, appointments = _load_data()

    doctor = doctors[doctors["Doctor_ID"].str.upper() == doctor_id.upper()]
    if doctor.empty:
        return []

    doctor = doctor.iloc[0]

    try:
        is_available = _is_doctor_available_on_day(
            doctor["Available_Days"], appointment_date
        )
    except ValueError:
        return []

    if not is_available:
        return []

    slots = pd.date_range(
        start=f"{appointment_date} {doctor['Start_Time']}",
        end=f"{appointment_date} {doctor['End_Time']}",
        freq="30min",
        inclusive="left",
    ).strftime("%H:%M").tolist()

    booked_slots = appointments[
        (appointments["Doctor_ID"].str.upper() == doctor_id.upper())
        & (appointments["Appointment_Date"] == appointment_date)
        & (appointments["Status"].str.lower() != "cancelled")
    ]["Appointment_Time"].tolist()

    return [slot for slot in slots if slot not in booked_slots]


def book_appointment(
    patient_id: str,
    doctor_id: str,
    appointment_date: str,
    appointment_time: str,
) -> str:
    patients, doctors, appointments = _load_data()

    patient = patients[patients["Patient_ID"].str.upper() == patient_id.upper()]
    doctor = doctors[doctors["Doctor_ID"].str.upper() == doctor_id.upper()]

    if patient.empty:
        return "Booking failed: patient ID was not found."

    if doctor.empty:
        return "Booking failed: doctor ID was not found."

    try:
        datetime.strptime(appointment_date, "%Y-%m-%d")
        datetime.strptime(appointment_time, "%H:%M")
    except ValueError:
        return "Booking failed: use date YYYY-MM-DD and time HH:MM."

    available_slots = get_available_slots(doctor_id, appointment_date)
    if appointment_time not in available_slots:
        return "Booking failed: this slot is unavailable."

    appointment_id = f"A{len(appointments) + 1:03d}"

    new_appointment = pd.DataFrame([{
        "Appointment_ID": appointment_id,
        "Patient_ID": patient_id.upper(),
        "Doctor_ID": doctor_id.upper(),
        "Appointment_Date": appointment_date,
        "Appointment_Time": appointment_time,
        "Status": "Confirmed",
    }])

    updated_appointments = pd.concat(
        [appointments, new_appointment],
        ignore_index=True,
    )
    updated_appointments.to_csv(APPOINTMENTS, index=False)

    return (
        f"Appointment confirmed: {appointment_id} | "
        f"{patient.iloc[0]['Patient_Name']} with "
        f"{doctor.iloc[0]['Doctor_Name']} on "
        f"{appointment_date} at {appointment_time}."
    )