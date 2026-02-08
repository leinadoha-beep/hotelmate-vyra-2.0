import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(message: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"You are Vyra, a polite hotel concierge.\nGuest: {message}"
    )

    return response.output_text
