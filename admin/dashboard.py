import json
import os

# Calea către fișierul cu răspunsuri
RESPONSES_PATH = os.path.join("personality", "responses.json")

# Încarcă răspunsurile
def load_responses():
    try:
        with open(RESPONSES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la încărcarea responses.json: {e}")
        return {}

def main():
    responses = load_responses()
    print("🤖 I-On e gata. Scrie ceva (sau 'exit' ca să închizi).")

    while True:
        user_input = input("TU 🧠: ").strip().lower()
        if user_input == "exit":
            print("I-On 🤖: La revedere, dragul meu!")
            break

        response = responses.get(user_input, "🤖 I-On: Încă nu știu ce să răspund la asta.")
        print(f"I-On 🤖: {response}")

if __name__ == "__main__":
    main()
