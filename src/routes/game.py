import random

from flask import Blueprint, render_template, request, session, url_for, jsonify
from flask_login import current_user, login_required

from src.services.scores import get_scoreboard, record_score

game_bp = Blueprint("game", __name__)


@game_bp.route("/game", methods=["GET", "POST"])
@login_required
def game():
    if "target_number" not in session:
        session["target_number"] = random.randint(0, 100)
    if "attempts" not in session:
        session["attempts"] = 0

    feedback = None
    feedback_type = None
    latest_score = None
    guess_value = ""

    if request.method == "POST":
        action = request.form.get("action", "guess")

        if action == "reset":
            session["target_number"] = random.randint(0, 100)
            session["attempts"] = 0
            feedback = "Neue Runde gestartet! Wir haben eine frische Zahl vorbereitet."
            feedback_type = "info"
            guess_value = ""
        else:
            guess_raw = request.form.get("guess", "").strip()
            guess_value = guess_raw
            if not guess_raw:
                feedback = "Bitte gib eine Zahl ein, bevor du rätst."
                feedback_type = "error"
            else:
                try:
                    guess = int(guess_raw)
                except ValueError:
                    feedback = "Ungültige Eingabe. Bitte gib eine ganze Zahl zwischen 0 und 100 ein."
                    feedback_type = "error"
                else:
                    if guess < 0 or guess > 100:
                        feedback = "Die Zahl sollte zwischen 0 und 100 liegen."
                        feedback_type = "error"
                    else:
                        session["attempts"] = session.get("attempts", 0) + 1
                        attempts = session["attempts"]
                        target_number = session["target_number"]

                        if guess < target_number:
                            feedback = f"{guess} ist zu niedrig. Versuch es mit einer höheren Zahl!"
                            feedback_type = "hint"
                        elif guess > target_number:
                            feedback = f"{guess} ist zu hoch. Versuch es mit einer niedrigeren Zahl!"
                            feedback_type = "hint"
                        else:
                            record_score(current_user.id, attempts)
                            latest_score = attempts
                            feedback = (
                                f"Treffer! Du hast die geheime Zahl {guess} nach {attempts} Versuchen gefunden. "
                                "Wir haben sofort eine neue Zahl für dich vorbereitet – viel Erfolg!"
                            )
                            feedback_type = "success"
                            session["target_number"] = random.randint(0, 100)
                            session["attempts"] = 0
                            guess_value = ""

    scoreboard = get_scoreboard(limit=5)

    # determine image based on attempts or win state
    def compute_image(attempts: int, won: bool = False) -> str:
        if won:
            return url_for("static", filename="img/soeder_win.png")
        index = min((attempts or 0) + 1, 12)
        return url_for("static", filename=f"img/soeder_{index}.png")

    image_url = compute_image(session.get("attempts", 0), won=(latest_score is not None))

    return render_template(
        "game.html",
        scoreboard=scoreboard,
        feedback=feedback,
        feedback_type=feedback_type,
        current_attempts=session.get("attempts", 0),
        latest_score=latest_score,
        guess_value=guess_value,
        image_url=image_url,
    )


@game_bp.route("/game/guess", methods=["POST"])
@login_required
def game_guess():
    if "target_number" not in session:
        session["target_number"] = random.randint(0, 100)
    if "attempts" not in session:
        session["attempts"] = 0

    feedback = None
    feedback_type = None
    latest_score = None

    guess_raw = request.form.get("guess", "").strip()
    if not guess_raw:
        feedback = "Bitte gib eine Zahl ein, bevor du rätst."
        feedback_type = "error"
        return _json_state(feedback, feedback_type, latest_score)

    try:
        guess = int(guess_raw)
    except ValueError:
        feedback = "Ungültige Eingabe. Bitte gib eine ganze Zahl zwischen 0 und 100 ein."
        feedback_type = "error"
        return _json_state(feedback, feedback_type, latest_score)

    if guess < 0 or guess > 100:
        feedback = "Die Zahl sollte zwischen 0 und 100 liegen."
        feedback_type = "error"
        return _json_state(feedback, feedback_type, latest_score)

    session["attempts"] = session.get("attempts", 0) + 1
    attempts = session["attempts"]
    target_number = session["target_number"]

    if guess < target_number:
        feedback = f"{guess} ist zu niedrig. Versuch es mit einer höheren Zahl!"
        feedback_type = "hint"
    elif guess > target_number:
        feedback = f"{guess} ist zu hoch. Versuch es mit einer niedrigeren Zahl!"
        feedback_type = "hint"
    else:
        record_score(current_user.id, attempts)
        latest_score = attempts
        feedback = (
            f"Treffer! Du hast die geheime Zahl {guess} nach {attempts} Versuchen gefunden. "
            "Wir haben sofort eine neue Zahl für dich vorbereitet — viel Erfolg!"
        )
        feedback_type = "success"
        session["target_number"] = random.randint(0, 100)
        session["attempts"] = 0

    return _json_state(feedback, feedback_type, latest_score)


@game_bp.route("/game/reset", methods=["POST"])
@login_required
def game_reset():
    session["target_number"] = random.randint(0, 100)
    session["attempts"] = 0
    feedback = "Neue Runde gestartet! Wir haben eine frische Zahl vorbereitet."
    feedback_type = "info"
    return _json_state(feedback, feedback_type)


def _json_state(feedback=None, feedback_type=None, latest_score=None, guess_value=""):
    scoreboard = get_scoreboard(limit=5)
    # image: show win image if just won; else by attempts
    won = latest_score is not None
    if won:
        image_url = url_for("static", filename="img/soeder_win.png")
    else:
        idx = min((session.get("attempts", 0) or 0) + 1, 12)
        image_url = url_for("static", filename=f"img/soeder_{idx}.png")

    return jsonify(
        {
            "feedback": feedback,
            "feedback_type": feedback_type,
            "current_attempts": session.get("attempts", 0),
            "latest_score": latest_score,
            "guess_value": guess_value,
            "image_url": image_url,
            "scoreboard_html": render_template("scoreboard_fragment.html", scoreboard=scoreboard),
        }
    )
