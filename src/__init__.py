from __future__ import annotations

import os
from typing import Optional

from flask import Flask

from src.db import init_app as init_db_app
from src.extensions import login_manager
from src.routes.auth import auth_bp
from src.routes.game import game_bp
from src.routes.main import main_bp
from src.services.users import get_user_by_id


def create_app(config: Optional[dict] = None) -> Flask:
    """
    Application factory, optionally accepting configuration overrides.
    """
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    env_secret = os.environ.get("FLASK_SECRET_KEY")
    env_database = os.environ.get("DATABASE_PATH")

    if env_secret:
        app.config["SECRET_KEY"] = env_secret
    if env_database:
        app.config["DATABASE"] = env_database

    if config:
        app.config.update(config)

    app.config.setdefault("SECRET_KEY", "change-me")
    app.config.setdefault("DATABASE", "soeder.db")

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
