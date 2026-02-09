import json
import os

# Calea către fișierul brain.json
BRAIN_PATH = os.path.join(os.path.dirname(__file__), "data", "brain.json")

# Încarcă întrebările și răspunsurile
with open(BRAIN_PATH, "r", encoding="utf-8") as file:
    brain_data = json.load(file)


def find_answer(question: str):
    """
    Returnează (answer, found_bool)
    - answer: string dacă a găsit
    - found_bool: True/False
    """
    q = (question or "").strip().lower()
    if not q:
        return None, False

    for item in brain_data:
        for k in item.get("questions", []):
            if k and k.lower() in q:
                return item.get("answer", ""), True

    return None, False
