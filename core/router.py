import json
import os

from core.brain import find_answer
from core.openai_client import ask_openai


# -----------------------------
# Load hotel data safely
# -----------------------------
def load_hotel_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(base_dir, "data", "hotel_data.json")

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


HOTEL_DATA = load_hotel_data()


# -----------------------------
# Build OpenAI prompt
# (used ONLY if local fails)
# -----------------------------
def build_openai_prompt(user_message: str) -> str:
    hotel_name = HOTEL_DATA.get("hotel_name", "the hotel")
    city = HOTEL_DATA.get("city", "")
    address = HOTEL_DATA.get("address", "")
    facilities = HOTEL_DATA.get("facilities", {})
    faq = HOTEL_DATA.get("faq", [])
    rules = HOTEL_DATA.get("rules", [])

    context = f"""
You are Vyra, the digital concierge for {hotel_name}.

Location:
- City: {city}
- Address: {address}

Hotel context (use ONLY if relevant):
- Facilities: {json.dumps(facilities, ensure_ascii=False)}
- Rules: {json.dumps(rules, ensure_ascii=False)}
- FAQ: {json.dumps(faq, ensure_ascii=False)}

IMPORTANT RULES:
1) Do NOT invent hotel-specific facts.
2) If asked about nearby places, answer GENERICALLY and ask for preferences.
3) Be concise, friendly, practical.

User question:
{user_message}
""".strip()

    return context


# -----------------------------
# MAIN ROUTER
# -----------------------------
def route_question(user_message: str):
    """
    Returns ALWAYS: (answer_text, source)
    source = "local" | "openai" | "fallback"
    """

    # ---- validate input
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "fallback",
        )

    user_message = user_message.strip()

    # ---- 1️⃣ LOCAL BRAIN FIRST (STRICT)
    local_answer = find_answer(user_message)

    if local_answer:
        # FORCE local answer, no OpenAI contamination
        return local_answer, "local"

    # ---- 2️⃣ OPENAI ONLY IF LOCAL FAILED
    try:
        prompt = build_openai_prompt(user_message)
        ai_answer = ask_openai(prompt)

        if ai_answer and ai_answer.strip():
            return ai_answer, "openai"

    except Exception:
        pass

    # ---- 3️⃣ SAFE FALLBACK
    return (
        "<strong>Message:</strong> I’m sorry, I can’t answer that right now. Please contact reception.<br>"
        "<strong>Nachricht:</strong> Leider kann ich diese Frage im Moment nicht beantworten. Bitte wenden Sie sich an die Rezeption.",
        "fallback",
    )
