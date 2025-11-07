from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from src.db import get_db


@dataclass
class User(UserMixin):
    id: int
    username: str
    password_hash: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            first_name=row["first_name"] or "",
            last_name=row["last_name"] or "",
            email=row["email"] or "",
        )


def get_user_by_id(user_id: int) -> Optional[User]:
    db = get_db()
    row = db.execute(
        """
        SELECT id, username, password_hash, first_name, last_name, email
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    return User.from_row(row) if row else None


def get_user_by_username(username: str) -> Optional[User]:
    db = get_db()
    row = db.execute(
        """
        SELECT id, username, password_hash, first_name, last_name, email
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()
    return User.from_row(row) if row else None


PASSWORD_HASH_METHOD = "pbkdf2:sha256"
PASSWORD_SALT_LENGTH = 16


def create_user(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: str,
) -> Optional[User]:
    password_hash = generate_password_hash(
        password,
        method=PASSWORD_HASH_METHOD,
        salt_length=PASSWORD_SALT_LENGTH,
    )
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO users (username, password_hash, first_name, last_name, email)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password_hash, first_name, last_name, email),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return None
    return get_user_by_username(username)
