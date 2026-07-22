from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PATIENT_DB = BASE_DIR / "database" / "patient_db.csv"


def get_patient_history(query: str) -> str:
    """Find a patient by Patient ID or name and return safe clinical details."""
    patients = pd.read_csv(PATIENT_DB, dtype=str).fillna("")
    query = query.strip().lower()

    match = patients[
        (patients["Patient_ID"].str.lower() == query)
        | (patients["Patient_Name"].str.lower().str.contains(query, na=False))
    ]

    if match.empty:
        return "No patient was found. Please check the Patient ID or name."

    if len(match) > 1:
        names = ", ".join(match["Patient_Name"].tolist())
        return f"More than one patient matched: {names}. Please use the Patient ID."

    patient = match.iloc[0]

    return f"""
Patient: {patient["Patient_Name"]} ({patient["Patient_ID"]})
Age/Gender: {patient["Age"]} / {patient["Gender"]}
Condition: {patient["Disease"]}
Medical history: {patient["Medical_History"]}
Current medication: {patient["Current_Medication"]}
Allergies: {patient["Allergies"]}
Last visit: {patient["Last_Visit"]}
Assigned doctor: {patient["Doctor_Assigned"]}
""".strip()