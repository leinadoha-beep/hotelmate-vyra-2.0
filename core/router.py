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


def _build_context(hotel_data: dict) -> str:
    """
    Construiește un context scurt și safe pentru OpenAI,
    ca să NU mai fabuleze cu restaurante din Madrid etc.
    """
    # Dacă hotel_data e gol, măcar ținem un guardrail minim.
    hotel_name = hotel_data.get("hotel_name", "the hotel")
    city = hotel_data.get("city", "")
    country = hotel_data.get("country", "")

    location_line = ", ".join([x for x in [city, country] if x]).strip()
    if location_line:
        location_line = f"Location: {location_line}"
    else:
        location_line = "Location: (unknown)"

    return (
        "You are Vyra, a digital concierge for a specific hotel.\n"
        "IMPORTANT RULES:\n"
        "1) If the user asks for places (restaurants/attractions), you MUST keep recommendations within the hotel's city/area.\n"
        "2) If the location is unknown or you are unsure, ask a short clarifying question instead of inventing places.\n"
        "3) Keep answers concise, helpful, and friendly.\n\n"
        f"Hotel: {hotel_name}\n"
        f"{location_line}\n"
    )


def route_question(user_message: str):
    """
    Returnează (answer, source)
    source: "local" | "openai" | "fallback"
    """
    user_message = (user_message or "").strip()
    if not user_message:
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "fallback",
        )

    # 1) Încercăm local (brain.json)
    local_answer, found = find_answer(user_message)
    if found and local_answer:
        return local_answer, "local"

    # 2) Dacă nu avem local, mergem la OpenAI cu context
    try:
        context = _build_context(HOTEL_DATA)
        answer = ask_openai(user_message, system_context=context)
        return answer, "openai"
    except Exception:
        # 3) fallback sigur dacă OpenAI pică
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen.",
            "fallback",
        )
