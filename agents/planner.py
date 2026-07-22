import re


def route_request(user_message: str) -> str:
    """Return the agent name best suited to handle a user request."""
    message = user_message.strip().lower()

    if not message:
        return "unknown"

    appointment_keywords = [
        "appointment", "book", "booking", "schedule",
        "slot", "availability", "available", "reschedule", "cancel",
    ]
    history_keywords = [
        "history", "medication", "medicine", "allergy", "allergies",
        "last visit", "patient record", "patient details",
    ]

    if any(keyword in message for keyword in appointment_keywords):
        return "appointment_agent"

    if any(keyword in message for keyword in history_keywords):
        return "history_agent"

    if re.search(r"\bp\d{3}\b", message):
        return "history_agent"

    return "medical_agent"