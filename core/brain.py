import json
import os
import re
import unicodedata
from typing import Optional, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

ACTIVE_HOTEL_PATH = os.path.join(DATA_DIR, "active_hotel.txt")
DEFAULT_HOTEL_SLUG = "niu_furth"  # fallback safe

def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    # remove diacritics
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # collapse spaces
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
    Loads hotel-specific knowledge.json based on active_hotel.txt:
      data/hotels/<slug>/knowledge.json
    Fallbacks:
      data/brain.json (legacy)
    """
    slug = _get_active_hotel_slug()
    hotel_knowledge_path = os.path.join(DATA_DIR, "hotels", slug, "knowledge.json")

    # 1) preferred: hotel knowledge.json
    try:
        with open(hotel_knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass

    # 2) legacy fallback: data/brain.json
    legacy_path = os.path.join(DATA_DIR, "brain.json")
    try:
        with open(legacy_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"legacy": data}
    except Exception:
        return {}

def find_answer(question: str) -> Optional[str]:
    if not question:
        return None

    q = _normalize(question)
    if not q:
        return None

    kb = _load_knowledge()

    # --- NEW SCHEMA: {"facts": {...}, "faq":[...]} ---
    facts = kb.get("facts") if isinstance(kb, dict) else None
    if isinstance(facts, dict):
        # keyword -> fact key
        fact_rules = [
            (["check in", "check-in", "checkin", "sosire", "intrare", "ora check in", "ora check-in"], "checkin"),
            (["check out", "check-out", "checkout", "plecare", "iesire", "ora check out", "ora check-out"], "checkout"),
            (["wifi", "wi fi", "internet"], "wifi"),
            (["parcare", "parking", "park"], "parking"),
            (["mic dejun", "breakfast", "micul dejun"], "breakfast"),  # dacă vrei să adaugi în facts
        ]
        for keywords, key in fact_rules:
            if any(k in q for k in keywords) and key in facts:
                val = facts.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

    faq = kb.get("faq") if isinstance(kb, dict) else None
    if isinstance(faq, list):
        for item in faq:
            if not isinstance(item, dict):
                continue
            qq = _normalize(item.get("q", ""))
            aa = item.get("a", "")
            tags = item.get("tags", [])
            tags_norm = [_normalize(t) for t in tags] if isinstance(tags, list) else []

            # match by faq question substring OR tag hit
            if (qq and (qq in q or q in qq)) or any(t and t in q for t in tags_norm):
                if isinstance(aa, str) and aa.strip():
                    return aa.strip()

    # --- LEGACY SCHEMA support (optional) ---
    legacy = kb.get("legacy")
    if isinstance(legacy, list):
        for item in legacy:
            if not isinstance(item, dict):
                continue
            qs = item.get("questions", [])
            ans = item.get("answer", "")
            if not isinstance(qs, list) or not isinstance(ans, str):
                continue
            for candidate in qs:
                if candidate and _normalize(candidate) in q:
                    return ans.strip() if ans else None

    return None
