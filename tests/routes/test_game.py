import pytest


def test_game_requires_authentication(client):
    response = client.get("/game")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_game_initializes_session_on_first_get(auth_client):
    client, _ = auth_client

    response = client.get("/game")
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "target_number" in session
        assert session["attempts"] == 0


def test_game_reset_action_resets_state(auth_client):
    client, _ = auth_client
    with client.session_transaction() as session:
        session["target_number"] = 17
        session["attempts"] = 3

    response = client.post("/game", data={"action": "reset"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Neue Runde gestartet" in response.data

    with client.session_transaction() as session:
        assert session["attempts"] == 0
        assert "target_number" in session


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"guess": ""}, "Bitte gib eine Zahl ein, bevor du r\u00e4tst.".encode("utf-8")),
        (
            {"guess": "abc"},
            "Ung\u00fcltige Eingabe. Bitte gib eine ganze Zahl zwischen 0 und 100 ein.".encode("utf-8"),
        ),
        ({"guess": "150"}, "Die Zahl sollte zwischen 0 und 100 liegen.".encode("utf-8")),
    ],
)
def test_game_rejects_invalid_input_without_incrementing_attempts(auth_client, payload, expected_message):
    client, _ = auth_client
    with client.session_transaction() as session:
        session["target_number"] = 50
        session["attempts"] = 0

    response = client.post("/game", data=payload, follow_redirects=True)
    assert expected_message in response.data

    with client.session_transaction() as session:
        assert session["attempts"] == 0


def test_game_provides_hint_and_counts_attempts(auth_client):
    client, _ = auth_client
    with client.session_transaction() as session:
        session["target_number"] = 80
        session["attempts"] = 0

    response = client.post("/game", data={"guess": "10"}, follow_redirects=True)
    assert "10 ist zu niedrig".encode("utf-8") in response.data

    with client.session_transaction() as session:
        assert session["attempts"] == 1


def test_game_records_score_and_resets_after_win(auth_client, monkeypatch):
    client, user = auth_client
    recorded = {}

    def fake_record_score(user_id, tries):
        recorded["user_id"] = user_id
        recorded["tries"] = tries

    monkeypatch.setattr("src.routes.game.record_score", fake_record_score)

    with client.session_transaction() as session:
        session["target_number"] = 33
        session["attempts"] = 0

    response = client.post("/game", data={"guess": "33"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Treffer!" in response.data
    assert recorded == {"user_id": user.id, "tries": 1}

    with client.session_transaction() as session:
        assert session["attempts"] == 0
        assert "target_number" in session


def test_game_passes_limit_to_scoreboard(auth_client, monkeypatch):
    client, _ = auth_client
    captured = {}

    def fake_get_scoreboard(*, limit=None):
        captured["limit"] = limit
        return []

    monkeypatch.setattr("src.routes.game.get_scoreboard", fake_get_scoreboard)

    response = client.get("/game")
    assert response.status_code == 200
    assert captured["limit"] == 5
