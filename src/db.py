from __future__ import annotations

import sqlite3
from typing import Optional

from flask import current_app, g

DEFAULT_DATABASE = "soeder.db"


def get_db() -> sqlite3.Connection:
    """
    Gets a database connection for the current application context.
    """
    if "db" not in g:
        database_path = current_app.config.get("DATABASE", DEFAULT_DATABASE)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(error: Optional[BaseException] = None) -> None:
    """
    Closes the database connection if it exists.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_user_columns(db: sqlite3.Connection) -> None:
    """
    Ensures that the 'users' table in the database contains the required columns.
    """
    existing_columns = {row["name"] for row in db.execute("PRAGMA table_info(users)")}
    required_columns = {
        "first_name": "TEXT",
        "last_name": "TEXT",
        "email": "TEXT",
    }
    for column, column_type in required_columns.items():
        if column not in existing_columns:
            db.execute(f"ALTER TABLE users ADD COLUMN {column} {column_type}")


def init_db() -> None:
    """
    Initializes the database by creating necessary tables if they do not exist.
    """
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


def init_app(app) -> None:
    """
    Initializes the database for the given Flask application.
    """
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
