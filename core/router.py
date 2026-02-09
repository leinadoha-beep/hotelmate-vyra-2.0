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
    """
    Aici punem contextul hotelului ca OpenAI să nu fabuleze despre Madrid :)
    """
    hotel_name = HOTEL_DATA.get("hotel_name", "this hotel")
    city = HOTEL_DATA.get("city", "")
    address = HOTEL_DATA.get("address", "")
    nearby = HOTEL_DATA.get("nearby", [])
    facilities = HOTEL_DATA.get("facilities", {})
    policies = HOTEL_DATA.get("policies", {})

    nearby_text = ""
    if isinstance(nearby, list) and nearby:
        nearby_text = "\n- " + "\n- ".join([str(x) for x in nearby[:20]])

    prompt = f"""
You are Vyra, the digital concierge of "{hotel_name}".
Location details:
- City: {city}
- Address: {address}

Hotel facilities/info (if available):
- Facilities: {facilities}
- Policies: {policies}
Nearby recommendations (if available): {nearby_text}

RULES:
1) If the guest asks for recommendations (restaurants, attractions, transport), prioritize options NEAR the hotel and in the same city/area. If city is unknown, ask a clarifying question.
2) Do NOT invent specific business names unless they are provided in hotel data. If not available, give categories + how to find nearby options + offer to ask reception.
3) Keep answers concise, helpful, friendly.

Guest question: {user_message}
""".strip()

    return prompt

def route_question(user_message: str):
    """
    Returnează (answer_html, source)
    source: "internal" | "openai" | "error"
    """
    # input safety
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "error"
        )

    # 1) Încercăm intern
    internal_answer, found = find_answer(user_message)
    if found and internal_answer.strip():
        return internal_answer, "internal"

    # 2) Dacă nu avem intern → OpenAI, dar cu context hotel
    try:
        prompt = _build_openai_prompt(user_message)
        answer = ask_openai(prompt)
        return answer, "openai"
    except Exception:
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen.",
            "error"
        )
