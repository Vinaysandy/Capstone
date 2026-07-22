from rag.retriever import retrieve_context

SAFETY_NOTE = (
    "\n\nImportant: This is general information only, not a diagnosis or "
    "medical prescription. Consult a qualified clinician for personal medical advice. "
    "For emergencies, contact emergency services immediately."
)


def answer_medical_question(question: str) -> str:
    """Answer only using relevant chunks from approved RAG documents."""
    if not question.strip():
        return "Please enter a medical question."

    results = retrieve_context(question)

    if not results:
        return (
            "I do not have enough approved medical information to answer that "
            "question. Please consult a qualified healthcare professional."
            + SAFETY_NOTE
        )

    approved_information = "\n\n".join(
        result["text"] for result in results
    )
    sources = ", ".join(sorted({result["source"] for result in results}))

    return (
        f"Based on the approved reference material:\n\n"
        f"{approved_information}\n\n"
        f"Sources: {sources}"
        + SAFETY_NOTE
    )