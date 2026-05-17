import json
import os

from core.brain import find_answer
from core.openai_client import ask_openai


def load_hotel_data():
    # hotel_data.json este în /data/hotel_data/hotel_data.json
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    hotel_data_path = os.path.join(base_dir, "data", "hotel_data", "hotel_data.json")

    try:
        with open(hotel_data_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


HOTEL_DATA = load_hotel_data()


def _build_hotel_context() -> str:
    """
    Build hotel context string for system prompt.
    """
    hotel_name = HOTEL_DATA.get("name", "the hotel")
    city = HOTEL_DATA.get("location", {}).get("city", "")
    address = HOTEL_DATA.get("location", {}).get("address", "")
    amenities = HOTEL_DATA.get("amenities", [])
    contact = HOTEL_DATA.get("contact", {})
    checkin = HOTEL_DATA.get("checkin", "14:00")
    checkout = HOTEL_DATA.get("checkout", "12:00")
    languages = HOTEL_DATA.get("languages_spoken", [])

    amenities_str = ", ".join(amenities) if amenities else "None listed"
    languages_str = ", ".join(languages) if languages else "English"

    context = f"""
YOU ARE: Vyra, a polite digital concierge for {hotel_name} in {city}.

HOTEL LOCATION:
- Name: {hotel_name}
- City: {city}
- Address: {address}
- Check-in: {checkin}
- Check-out: {checkout}
- Contact: {contact.get('telefon', 'N/A')} | {contact.get('email', 'N/A')}
- Languages: {languages_str}

AMENITIES AVAILABLE:
{amenities_str}

=== STRICT RULES ===
1. YOU CAN ONLY discuss information explicitly listed above about THIS hotel.
2. DO NOT invent restaurant names, addresses, or make reservations.
3. DO NOT hallucinate dining options, attractions, or nearby services.
4. If asked about restaurants, dining, or external services:
   - Say: "I don't have information about external restaurants. Please ask the front desk."
5. DO NOT make up conversation history or previous exchanges.
6. Only respond about: check-in/out times, amenities, contact info, hotel policies.
7. Keep responses short, factual, and helpful.
8. If asked about something not listed above, say: "I don't have that information. Please contact the front desk at {contact.get('telefon', 'reception')}."
""".strip()

    return context


def route_question(user_message: str, interaction_count: int = 0, conversation_history: list = None):
    """
    Route question through knowledge base and AI with interaction tracking.
    
    Args:
        user_message: Guest's question
        interaction_count: Current number of interactions in this session
        conversation_history: List of {'role': str, 'content': str} dicts
    
    Returns:
        Tuple: (answer_text, source)
        source = "local" | "openai" | "fallback"
    """
    if conversation_history is None:
        conversation_history = []
    
    # validare input
    if not user_message or not user_message.strip():
        return (
            "<strong>Message:</strong> Please type a question.<br>"
            "<strong>Nachricht:</strong> Bitte geben Sie eine Frage ein.",
            "fallback",
        )

    user_message = user_message.strip()

    # 1) ALWAYS try Local (brain) first
    local_answer = find_answer(user_message)
    if local_answer:
        return local_answer, "local"

    # 2) Check if interaction limit reached (10 interactions)
    # If yes, return local-only message instead of trying OpenAI
    if interaction_count >= 10:
        return "Conversation context lost.Returning to local model", "local"

    # 3) OpenAI (only if limit not reached)
    try:
        # Include hotel context with conversation history
        hotel_context = _build_hotel_context()
        answer = ask_openai(user_message, conversation_history, hotel_context)
        return answer, "openai"
    except Exception:
        # fallback sigur
        return (
            "<strong>Message:</strong> Temporary AI issue. Please try again later.<br>"
            "<strong>Nachricht:</strong> Temporäres KI-Problem. Bitte später erneut versuchen.",
            "fallback",
        )
