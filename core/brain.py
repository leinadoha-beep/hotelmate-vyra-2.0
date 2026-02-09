import json
import os

BRAIN_PATH = os.path.join(os.path.dirname(__file__), "data", "brain.json")

def find_answer(question: str):
    """
    Returnează (answer, found_bool)
    found_bool = True dacă am găsit un răspuns intern.
    """
    question_lower = (question or "").lower().strip()

    try:
        with open(BRAIN_PATH, "r", encoding="utf-8") as file:
            brain_data = json.load(file)
    except Exception:
        brain_data = []

    for item in brain_data:
        for q in item.get("questions", []):
            if q.lower() in question_lower:
                return item.get("answer", ""), True

    # NU am găsit intern
    return "", False
