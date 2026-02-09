import json
import os

from core.brain import find_answer
from core.openai_client import ask_openai

def load_hotel_data():
    hotel_data_path = os.path.join("data", "hotel_data.json")
    try:
        with open(hotel_data_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

HOTEL_DATA = load_hotel_data()

def _build_openai_prompt(user_message: str) -> str:
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

Hotel context (use ONLY this when possible):
- Facilities: {json.dumps(facilities, ensure_ascii=False)}
- Rules: {json.dumps(rules, ensure_ascii=False)}
- FAQ: {json.dumps(faq, ensure_ascii=False)}

Important rules:
1) If the user asks about nearby places (restaurants, attractions), recommend options GENERICALLY and ask for the user's preference,
   but DO NOT invent exact business names unless they exist in HOTEL_DATA.
2) Be concise, friendly, and practical.
3) If you lack specifics, propose safe next steps (ask reception, provide general guidance).
User question: {user_message}
""".strip()

    return context

def route_question(user_message: str):
    """
    Returnează mereu: (answer_text, source)
    source = "local" | "openai" | "fallback"
    """
    # validare input
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "fallback"
        )

    user_message = user_message.strip()

    # 1) răspuns local (brain)
    local_answer = find_answer(user_message)
    if local_answer:
        return local_answer, "local"

    # 2) OpenAI
    try:
        prompt = _build_openai_prompt(user_message)
        answer = ask_openai(prompt)
        return answer, "openai"
    except Exception:
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen.",
            "fallback"
        )
