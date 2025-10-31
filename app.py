import random
import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash, session, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

DATABASE = "soeder.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, password_hash, first_name, last_name, email):
        self.id = user_id  # Flask-Login checks this attribute
        self.username = username
        self.password_hash = password_hash
        self.first_name = first_name or ""
        self.last_name = last_name or ""
        self.email = email or ""

    @classmethod
    def from_row(cls, row):
        return cls(
            row["id"],
            row["username"],
            row["password_hash"],
            row["first_name"],
            row["last_name"],
            row["email"],
        )


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT
        )
        """
    )
    ensure_user_columns(db)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tries INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """
    )
    db.commit()


def ensure_user_columns(db):
    existing_columns = {row["name"] for row in db.execute("PRAGMA table_info(users)")}
    required_columns = {
        "first_name": "TEXT",
        "last_name": "TEXT",
        "email": "TEXT",
    }
    for column, column_type in required_columns.items():
        if column not in existing_columns:
            db.execute(f"ALTER TABLE users ADD COLUMN {column} {column_type}")


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, first_name, last_name, email FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return User.from_row(row) if row else None


def get_user_by_username(username):
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, first_name, last_name, email FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return User.from_row(row) if row else None


def create_user(username, password, first_name, last_name, email):
    password_hash = generate_password_hash(password)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, first_name, last_name, email),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return None
    return get_user_by_username(username)


def record_score(user_id, tries):
    if user_id is None:
        raise ValueError("user_id is required to record a score")
    if tries is None:
        raise ValueError("tries is required to record a score")
    db = get_db()
    db.execute(
        "INSERT INTO scores (user_id, tries) VALUES (?, ?)",
        (user_id, int(tries)),
    )
    db.commit()


def get_scoreboard(limit=None):
    db = get_db()
    query = """
        SELECT
            u.id AS user_id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            s.tries,
            s.created_at
        FROM users u
        JOIN scores s ON s.user_id = u.id
        WHERE s.tries = (
            SELECT MIN(s2.tries)
            FROM scores s2
            WHERE s2.user_id = u.id
        )
        AND s.created_at = (
            SELECT MIN(s3.created_at)
            FROM scores s3
            WHERE s3.user_id = u.id AND s3.tries = s.tries
        )
        ORDER BY s.tries ASC, s.created_at ASC
    """
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (int(limit),)
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_soeder_image_url(attempts: int, won: bool = False):
    """Return the static URL for the soeder image based on attempts or win state.

    - At start (attempts == 0) -> soeder_1.png
    - Each attempt increases the index: attempts=1 -> soeder_2.png, ...
    - Max index is 12 -> soeder_12.png
    - If won is True -> soeder_win.png
    """
    if won:
        filename = "img/soeder_win.png"
    else:
        index = min(attempts + 1, 12)
        filename = f"img/soeder_{index}.png"
    return url_for("static", filename=filename)


@app.route("/")
def home():
    scoreboard = get_scoreboard(limit=5)
    return render_template("index.html", scoreboard=scoreboard)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("home"))

        flash("Ungültiger Benutzername oder Passwort", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not password:
            flash("Bitte einen Benutzernamen und ein Passwort eingeben", "error")
        elif not first_name or not last_name or not email:
            flash("Bitte Vorname, Nachname und E-Mail angeben", "error")
        elif password != confirm:
            flash("Passwörter stimmen nicht überein", "error")
        elif create_user(username, password, first_name, last_name, email) is None:
            flash("Benutzername ist bereits vergeben", "error")
        else:
            flash("Registrierung erfolgreich. Bitte einloggen.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/game", methods=["GET", "POST"])
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
    # determine image URL (win takes precedence)
    if latest_score is not None:
        image_url = get_soeder_image_url(0, won=True)
    else:
        image_url = get_soeder_image_url(session.get("attempts", 0), won=False)

    # If this was an AJAX request, return JSON so the client can update without a full reload
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or (
        request.headers.get("Accept", "").find("application/json") != -1
    )
    if is_ajax:
        return jsonify(
            {
                "feedback": feedback,
                "feedback_type": feedback_type,
                "current_attempts": session.get("attempts", 0),
                "latest_score": latest_score,
                "guess_value": guess_value,
                "image_url": image_url,
                # return rendered scoreboard fragment so the client can replace it easily
                "scoreboard_html": render_template("scoreboard_fragment.html", scoreboard=scoreboard),
            }
        )

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


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
