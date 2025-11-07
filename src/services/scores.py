from __future__ import annotations

from typing import List, Optional

from src.db import get_db


def record_score(user_id: int, tries: int) -> None:
    if user_id is None:
        raise ValueError("user_id is erforderlich, um einen Score zu speichern")
    if tries is None:
        raise ValueError("tries ist erforderlich, um einen Score zu speichern")

    db = get_db()
    db.execute(
        "INSERT INTO scores (user_id, tries) VALUES (?, ?)",
        (user_id, int(tries)),
    )
    db.commit()


def get_scoreboard(limit: Optional[int] = None) -> List[dict]:
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
