import json
import os

# Calea către fișierul brain.json
BRAIN_PATH = os.path.join(os.path.dirname(__file__), "data", "brain.json")

# Încarcă întrebările și răspunsurile
with open(BRAIN_PATH, "r", encoding="utf-8") as file:
    brain_data = json.load(file)

def find_answer(question: str) -> str:
    question_lower = question.lower().strip()
    for item in brain_data:
        for q in item["questions"]:
            if q in question_lower:
                return item["answer"]
    return "Îmi pare rău, nu am găsit un răspuns pentru întrebarea dvs. Doriți să contactez recepția?"
