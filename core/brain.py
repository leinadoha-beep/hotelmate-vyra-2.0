import json
import os

# Calea corectă: /data/brain.json (la rădăcina proiectului)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAIN_PATH = os.path.join(BASE_DIR, "data", "brain.json")


def _load_brain_data() -> list:
    """
    Încarcă brain.json.
    IMPORTANT: nu trebuie să crape aplicația dacă fișierul lipsește pe Render.
    """
    try:
        with open(BRAIN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except Exception:
        return []


BRAIN_DATA = _load_brain_data()


def find_answer(question: str) -> str | None:
    if not question:
        return None

    q = question.lower().strip()
    if not q:
        return None

    for item in BRAIN_DATA:
        qs = item.get("questions", [])
        ans = item.get("answer", "")
        for candidate in qs:
            if candidate and candidate.lower() in q:
                return ans

    return None
