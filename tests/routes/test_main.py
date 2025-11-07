def test_home_shows_empty_state_when_no_scores(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Noch keine Eintr\xc3\xa4ge" in response.data


def test_home_renders_scoreboard_entries(monkeypatch, client):
    captured = {}

    def fake_get_scoreboard(*, limit=None):
        captured["limit"] = limit
        return [
            {
                "username": "lena",
                "first_name": "Lena",
                "last_name": "Lustig",
                "tries": 2,
                "created_at": "2024-01-01 00:00:00",
                "user_id": 1,
            }
        ]

    monkeypatch.setattr("src.routes.main.get_scoreboard", fake_get_scoreboard)

    response = client.get("/")
    assert response.status_code == 200
    assert captured["limit"] == 5
    assert b"Lena Lustig" in response.data
    assert b"2 Versuche" in response.data
