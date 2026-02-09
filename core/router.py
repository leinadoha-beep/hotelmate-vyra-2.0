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


def route_question(user_message: str):
    """
    Router central Vyra.
    Returnează (answer_html, source) unde source este: 'local' sau 'openai'
    """
    # Siguranță input
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "local",
        )

    # 1) Încercăm răspuns local (brain.json)
    local_answer = find_answer(user_message)
    # În brain.py ai un fallback text fix când nu găsește răspuns.
    # Îl detectăm și considerăm că NU e un răspuns real.
    fallback_text = "Îmi pare rău, nu am găsit un răspuns"
    if local_answer and (fallback_text.lower() not in local_answer.lower()):
        return local_answer, "local"

    # 2) Dacă nu avem local, mergem la OpenAI
    try:
        answer = ask_openai(user_message)
        return answer, "openai"
    except Exception:
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen.",
            "local",
        )
