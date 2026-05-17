from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, session, redirect, url_for
from core.router import route_question

app = Flask(__name__)

# Required for Flask sessions (for production we will move this to an env var)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "vyra_dev_secret_key_change_me")


@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        
        # Initialize session variables on first request
        if "interaction_count" not in session:
            session["interaction_count"] = 0
        if "conversation_history" not in session:
            session["conversation_history"] = []
        
        # Get current state
        current_interaction_count = session["interaction_count"]
        conversation_history = session["conversation_history"]
        
        # Route the question
        bot_response, response_source = route_question(
            user_message, 
            current_interaction_count, 
            conversation_history
        )
        
        # Update conversation history ONLY if not at limit yet
        if current_interaction_count < 10:
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": bot_response})
            session["conversation_history"] = conversation_history
        
        # Increment interaction count for next request
        session["interaction_count"] = current_interaction_count + 1
        session.modified = True  # Explicitly mark session as modified
        
        # Store last exchange for display
        session["last_user_message"] = user_message
        session["last_bot_response"] = bot_response
        session["last_response_source"] = response_source

        # PRG pattern: avoid showing POST page on refresh
        return redirect(url_for("chat"))

    # GET: show the last exchange only once, then clear it (fresh on refresh)
    user_message = session.pop("last_user_message", "")
    bot_response = session.pop("last_bot_response", None)
    response_source = session.pop("last_response_source", None)

    return render_template(
        "index.html",
        bot_response=bot_response,
        response_source=response_source,
        user_message=user_message
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
