from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import engine

app = Flask(__name__)
# NOTE: Set any random secret key before production. This is just a placeholder.
app.secret_key = "replace-me-with-a-random-secret"
app.permanent_session_lifetime = timedelta(hours=6)


def _get_state():
    if "state" not in session:
        session["state"] = engine.initial_state()
    if "history" not in session:
        session["history"] = []
    return session["state"], session["history"]


def _set_state(state, history):
    session["state"] = state
    session["history"] = history


@app.route("/", methods=["GET", "POST"])
def index():
    state, history = _get_state()

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        # step the engine
        output, state = engine.step(state, user_input)
        history.append({"role": "user", "text": user_input})
        if output:
            history.append({"role": "system", "text": output})
        _set_state(state, history)
        return redirect(url_for("index"))

    # If first load, show the initial prompt
    if not history:
        initial_text, state = engine.step(state, "")
        history.append({"role": "system", "text": initial_text})
        _set_state(state, history)

    return render_template("index.html", history=history)


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Local run: python app.py
    app.run(host="0.0.0.0", port=8000, debug=True)
