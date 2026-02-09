import json
import os

# brain.json este în /data la rădăcina proiectului (src/data/brain.json pe Render)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # .../src
BRAIN_PATH = os.path.join(PROJECT_ROOT, "data", "brain.json")

def _load_brain():
    try:
        with open(BRAIN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # dacă lipsește, nu crăpăm aplicația; doar nu avem răspuns local
        return []
    except Exception:
        return []

brain_data = _load_brain()

def find_answer(question: str):
    """Returnează string dacă găsește răspuns local, altfel None."""
    if not question:
        return None

    q = question.lower().strip()

    for item in brain_data:
        for variant in item.get("questions", []):
            if variant and variant.lower() in q:
                return item.get("answer")

    return None
