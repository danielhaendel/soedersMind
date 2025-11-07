from flask import Blueprint, render_template

from src.services.scores import get_scoreboard

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    scoreboard = get_scoreboard(limit=5)
    return render_template("index.html", scoreboard=scoreboard)
