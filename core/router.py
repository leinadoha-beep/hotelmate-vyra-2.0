import json
import os

from core.openai_client import ask_openai


def load_hotel_data():
    hotel_data_path = os.path.join("data", "hotel_data.json")
    try:
        with open(hotel_data_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


HOTEL_DATA = load_hotel_data()


def route_question(user_message: str) -> str:
    """
    Router central Vyra.
    Decide dacă răspunde local sau prin OpenAI.
    """

    # 🔒 Siguranță input
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein."
        )

    # 🤖 OpenAI LIVE
    try:
        answer = ask_openai(user_message)
        return answer

    except Exception as e:
        # fallback sigur dacă OpenAI pică
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen."
        )
