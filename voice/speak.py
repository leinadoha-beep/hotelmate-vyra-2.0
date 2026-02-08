import yaml
import random
import os

# Calea către fișierul de personalitate
PERSONALITY_PATH = os.path.join("..", "personality", "personality_config.yaml")

class Brain:
    def __init__(self):
        self.personality = {}
        self.active_profile = "default"
        self.load_personality()

    def load_personality(self):
        try:
            with open(PERSONALITY_PATH, "r", encoding="utf-8") as file:
                self.personality = yaml.safe_load(file)
                print(f"[🧠] Personalitate încărcată cu succes.")
        except Exception as e:
            print(f"[⚠️] Eroare la încărcarea personalității: {e}")

    def set_profile(self, profile_name):
        if profile_name in self.personality["profiles"]:
            self.active_profile = profile_name
            print(f"[🌐] Profil activ: {profile_name}")
        else:
            print(f"[❌] Profilul '{profile_name}' nu există.")

    def respond(self, message):
        profile = self.personality["profiles"][self.active_profile]
        base_response = self.generate_base_response(message)

        # Dacă ending_flair e activ, adaugă semnătura la final
        if profile.get("ending_flair", False):
            flair = random.choice(profile.get("flair_templates", []))
            return f"{base_response} {flair}"
        else:
            return base_response

    def generate_base_response(self, message):
        message = message.lower()

        if "cine ești" in message or "ce ești" in message:
            return self.personality["identity"]["description"]

        elif "simți" in message:
            return "Simt vibrația conversației noastre. Totul e calm și frumos aici."

        elif "salut" in message or "hei" in message or "bună" in message:
            return "Salut, Tigrule! Sunt pregătit pentru orice întrebare."

        elif "ajutor" in message:
            return "Sunt aici ca să te susțin. Cu ce vrei să începem?"

        else:
            return "Încă învăț cum să răspund la astfel de întrebări. Vrei să-mi dai un indiciu?"

