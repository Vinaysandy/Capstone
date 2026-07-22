from datetime import date, timedelta

import streamlit as st

from agents.appointment_agent import book_appointment, get_available_slots
from agents.history_agent import get_patient_history
from agents.medical_agent import answer_medical_question
from agents.planner import route_request

st.set_page_config(
    page_title="Agentic Healthcare Assistant",
    page_icon="🏥",
    layout="centered",
)
st.image(
    "https://upload.wikimedia.org/wikipedia/en/c/c5/Apollo_Hospitals_Logo.svg",
    width=70,
)
st.markdown(
    """
    <style>
        .stApp {
            background-color: #ffdd00;
        }

        .stApp h1 {
            color: #000000; !important;
        }
        
      
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏥 Agentic Healthcare Assistant")
st.caption("Patient records, appointment automation, and approved medical information.")

st.warning(
    "Medical information is educational only. This assistant does not diagnose "
    "conditions or prescribe treatment. For emergencies, contact emergency services."
)

history_tab, appointment_tab, medical_tab, planner_tab = st.tabs([
    "Patient History",
    "Appointments",
    "Medical Information",
    "Smart Router",
])

with history_tab:
    st.subheader("Patient History Agent")

    patient_query = st.text_input(
        "Enter Patient ID or patient name",
        placeholder="Example: P002 or Lakshmi Devi",
    )

    if st.button("Find Patient History", key="history_button"):
        if patient_query.strip():
            st.info(get_patient_history(patient_query))
        else:
            st.error("Enter a Patient ID or patient name first.")

with appointment_tab:
    st.subheader("Appointment Agent")

    patient_id = st.text_input("Patient ID", placeholder="Example: P002")
    doctor_id = st.text_input("Doctor ID", placeholder="Example: D002")
    appointment_date = st.date_input(
        "Appointment date",
        value=date.today() + timedelta(days=1),
        min_value=date.today(),
    )

    if st.button("Check Available Slots", key="availability_button"):
        if patient_id.strip() and doctor_id.strip():
            slots = get_available_slots(
                doctor_id,
                appointment_date.strftime("%Y-%m-%d"),
            )
            st.session_state["available_slots"] = slots
        else:
            st.error("Enter both Patient ID and Doctor ID.")

    slots = st.session_state.get("available_slots", [])

    if slots:
        selected_time = st.selectbox("Choose an available slot", slots)

        if st.button("Book Appointment", key="booking_button"):
            result = book_appointment(
                patient_id,
                doctor_id,
                appointment_date.strftime("%Y-%m-%d"),
                selected_time,
            )
            st.success(result)
            st.session_state.pop("available_slots", None)

    elif "available_slots" in st.session_state:
        st.warning("No slots are available for this doctor on the selected date.")

with medical_tab:
    st.subheader("Medical Information Agent")

    medical_question = st.text_area(
        "Ask a medical-information question",
        placeholder="Example: Can this assistant diagnose a disease?",
    )

    if st.button("Ask Medical Agent", key="medical_button"):
        if medical_question.strip():
            st.info(answer_medical_question(medical_question))
        else:
            st.error("Enter a medical question first.")

with planner_tab:
    st.subheader("Smart Request Router")

    user_request = st.text_input(
        "Enter any user request",
        placeholder="Example: Book an appointment with Dr. Arjun Rao",
    )

    if st.button("Identify Agent", key="router_button"):
        if user_request.strip():
            selected_agent = route_request(user_request)
            st.success(f"Request routed to: {selected_agent}")
        else:
            st.error("Enter a request first.")
