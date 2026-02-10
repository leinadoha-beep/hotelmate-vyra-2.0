import json
import os
from difflib import SequenceMatcher

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOTELS_DIR = os.path.join(BASE_DIR, "data", "hotels")
ACTIVE_FILE = os.path.join(HOTELS_DIR, "active_hotel.txt")

def _load_active_hotel():
    try:
        with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None

def _load_knowledge():
    hotel = _load_active_hotel()
    if not hotel:
        return {}

    path = os.path.join(HOTELS_DIR, hotel, "knowledge.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

KB = _load_knowledge()

def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_answer(question: str) -> str | None:
    if not question:
        return None

    q = question.lower().strip()
    if not q:
        return None

    # 1) FACTS (fast path)
    for key, value in KB.get("facts", {}).items():
        if key in q:
            return value

    # 2) FAQ (similarity + tags)
    best_score = 0.0
    best_answer = None

    for item in KB.get("faq", []):
        score = _similar(q, item.get("q", ""))
        if any(tag in q for tag in item.get("tags", [])):
            score += 0.15

        if score > best_score and score >= 0.72:
            best_score = score
            best_answer = item.get("a")

    return best_answer
