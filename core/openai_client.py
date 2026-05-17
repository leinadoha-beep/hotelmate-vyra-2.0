import os
from openai import OpenAI
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(message: str, conversation_history: List[Dict] = None, hotel_context: str = "") -> str:
    """
    Call OpenAI API with conversation history and hotel context.
    
    Args:
        message: Current user message
        conversation_history: List of dicts with 'role' and 'content' keys
                             Includes full conversation context
        hotel_context: Hotel information, facilities, rules, and FAQ context string
    
    Returns:
        Response text from OpenAI
    """
    if conversation_history is None:
        conversation_history = []
    
    # Build system prompt with hotel context
    system_prompt = f"{hotel_context}".strip()
    
    # Build messages list with conversation context
    messages = [
        {
            "role": "system",
            "content": system_prompt
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
