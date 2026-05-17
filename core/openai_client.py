import os
from openai import OpenAI
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(message: str, conversation_history: List[Dict] = None) -> str:
    """
    Call OpenAI API with optional conversation history.
    
    Args:
        message: Current user message
        conversation_history: List of dicts with 'role' and 'content' keys
                             Includes full conversation context
    
    Returns:
        Response text from OpenAI
    """
    if conversation_history is None:
        conversation_history = []
    
    # Build messages list with conversation context
    messages = [
        {
            "role": "system",
            "content": "You are Vyra, a polite and helpful hotel concierge."
        }
    ]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback for API changes
        print(f"OpenAI API error: {e}")
        raise
