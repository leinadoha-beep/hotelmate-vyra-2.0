from dotenv import load_dotenv
load_dotenv()
import os


from flask import Flask, render_template, request
from core.router import route_question

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def chat():
    # ⛔ NU trimitem niciun răspuns la load simplu!
    if request.method == "GET":
        return render_template("index.html", bot_response=None)

    # ⛔ Procesăm doar mesajele trimise prin formular
    user_message = request.form.get("message", "")
    user_message = user_message.strip() if user_message else ""

    # Router decide răspunsul (offline / online / fallback)
    bot_response = route_question(user_message)

    return render_template("index.html", bot_response=bot_response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

