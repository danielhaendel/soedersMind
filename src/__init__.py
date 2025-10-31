import os

from flask import Flask

from src.db import init_app as init_db_app
from src.extensions import login_manager
from src.routes.auth import auth_bp
from src.routes.game import game_bp
from src.routes.main import main_bp
from src.services.users import get_user_by_id


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    secret_key = os.environ.get("FLASK_SECRET_KEY") or app.config.get("SECRET_KEY")
    database_path = os.environ.get("DATABASE_PATH") or app.config.get("DATABASE")

    if not secret_key:
        secret_key = "change-me"
    if not database_path:
        database_path = "soeder.db"

    app.config["SECRET_KEY"] = secret_key
    app.config["DATABASE"] = database_path

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return get_user_by_id(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    init_db_app(app)

    return app
