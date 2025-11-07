import pytest

from src.services.scores import get_scoreboard, record_score
from src.services.users import (
    PASSWORD_HASH_METHOD,
    create_user,
    get_user_by_username,
)


def test_create_user_persists_and_can_be_fetched(app_ctx):
    user = create_user(
        username="alice",
        password="super-secret",
        first_name="Alice",
        last_name="Tester",
        email="alice@example.com",
    )

    assert user is not None
    assert user.username == "alice"

    fetched = get_user_by_username("alice")
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.first_name == "Alice"
    assert fetched.password_hash.startswith(f"{PASSWORD_HASH_METHOD}:")


def test_create_user_duplicate_returns_none(app_ctx):
    create_user(
        username="bob",
        password="password1",
        first_name="Bob",
        last_name="Builder",
        email="bob@example.com",
    )

    duplicate = create_user(
        username="bob",
        password="password2",
        first_name="Robert",
        last_name="Builder",
        email="robert@example.com",
    )

    assert duplicate is None


def test_record_score_returns_best_attempt_only(app_ctx):
    user = create_user(
        username="carla",
        password="pw",
        first_name="Carla",
        last_name="Coder",
        email="carla@example.com",
    )

    record_score(user.id, 5)
    record_score(user.id, 3)
    record_score(user.id, 7)

    scoreboard = get_scoreboard()
    assert len(scoreboard) == 1
    entry = scoreboard[0]
    assert entry["tries"] == 3
    assert entry["first_name"] == "Carla"


def test_record_score_requires_user_id(app_ctx):
    with pytest.raises(ValueError):
        record_score(None, 5)
