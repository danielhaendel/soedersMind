from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from src.services.users import create_user, get_user_by_username

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("main.home"))

        flash("Ungültiger Benutzername oder Passwort", "error")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

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
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
