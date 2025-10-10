import sqlite3
from flask import Flask, render_template, g, redirect, url_for, request, flash
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
app.config["SECRET_KEY"] = "change-me"  # replace with a secure secret in production

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


@app.route("/")
@login_required
def home():
    return render_template(
        "index.html",
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
    )


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


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
