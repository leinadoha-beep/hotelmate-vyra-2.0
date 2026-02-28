import json
import os
import re
import unicodedata
from typing import Optional, Dict, Any

# =========================
# CONFIG
# =========================

DEBUG = True  # pune False când vrei producție

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

ACTIVE_HOTEL_PATH = os.path.join(DATA_DIR, "active_hotel.txt")
DEFAULT_HOTEL_SLUG = "niu_furth"  # fallback safe


# =========================
# UTILS
# =========================

def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\s+", " ", text)
    return text


def _get_active_hotel_slug() -> str:
    try:
        with open(ACTIVE_HOTEL_PATH, "r", encoding="utf-8") as f:
            slug = f.read().strip()
            return slug or DEFAULT_HOTEL_SLUG
    except Exception:
        return DEFAULT_HOTEL_SLUG


def _load_knowledge() -> Dict[str, Any]:
    """
    Ordine:
    1. data/hotels/<slug>/knowledge.json
    2. data/brain.json (legacy)
    """
    slug = _get_active_hotel_slug()
    hotel_knowledge_path = os.path.join(DATA_DIR, "hotels", slug, "knowledge.json")

    # 1) hotel-specific
    try:
        with open(hotel_knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass

    # 2) legacy fallback
    legacy_path = os.path.join(DATA_DIR, "brain.json")
    try:
        with open(legacy_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"legacy": data}
    except Exception:
        return {}


# =========================
# CORE LOGIC
# =========================

def find_answer(question: str) -> Optional[str]:
    if not question or not question.strip():
        return None

    q = _normalize(question)
    if not q:
        return None

    kb = _load_knowledge()

    # -------------------------
    # FACTS (STRICT)
    # -------------------------
    facts = kb.get("facts") if isinstance(kb, dict) else None

    if isinstance(facts, dict):
        fact_rules = [
            (["check in", "check-in", "checkin", "ora check in", "sosire", "intrare"], "checkin"),
            (["check out", "check-out", "checkout", "ora check out", "plecare", "iesire"], "checkout"),
            (["wifi", "wi fi", "internet"], "wifi"),
            (["parcare", "parking", "park"], "parking"),
            (["mic dejun", "breakfast"], "breakfast"),
        ]

        for keywords, key in fact_rules:
            if any(k in q for k in keywords) and key in facts:
                val = facts.get(key)
                if isinstance(val, str) and val.strip():
                    if DEBUG:
                        return f"[LOCAL:fact:{key}] {val.strip()}"
                    return val.strip()

    # -------------------------
    # FAQ (MATCH Q OR TAGS)
    # -------------------------
    faq = kb.get("faq") if isinstance(kb, dict) else None

    if isinstance(faq, list):
        for item in faq:
            if not isinstance(item, dict):
                continue

            q_faq = _normalize(item.get("q", ""))
            a_faq = item.get("a", "")
            tags = item.get("tags", [])

            tags_norm = [_normalize(t) for t in tags if isinstance(t, str)]

            if (
                (q_faq and q_faq in q)
                or any(t and t in q for t in tags_norm)
            ):
                if isinstance(a_faq, str) and a_faq.strip():
                    if DEBUG:
                        return f"[LOCAL:faq] {a_faq.strip()}"
                    return a_faq.strip()

    # -------------------------
    # LEGACY SUPPORT
    # -------------------------
    legacy = kb.get("legacy")

    if isinstance(legacy, list):
        for item in legacy:
            if not isinstance(item, dict):
                continue

            questions = item.get("questions", [])
            answer = item.get("answer", "")

            if not isinstance(answer, str):
                continue

            for candidate in questions:
                if candidate and _normalize(candidate) in q:
                    if DEBUG:
                        return f"[LOCAL:legacy] {answer.strip()}"
                    return answer.strip()

    # -------------------------
    # NOTHING FOUND → EXTERNAL
    # -------------------------
    return None
