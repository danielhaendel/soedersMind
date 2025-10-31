from src.services.users import create_user


def register_user(app):
    with app.app_context():
        return create_user(
            username="testuser",
            password="secret123",
            first_name="Test",
            last_name="Tester",
            email="test@example.com",
        )


def test_register_and_login_flow(client):
    # Registration page reachable
    response = client.get("/register")
    assert response.status_code == 200

    # Successful registration redirects to login with flashed message
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "password": "geheim123",
            "confirm": "geheim123",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registrierung erfolgreich" in response.data

    # Login with the new account succeeds
    response = client.post(
        "/login",
        data={"username": "newuser", "password": "geheim123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Eingeloggt als" in response.data


def test_game_requires_authentication(client):
    response = client.get("/game")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_game_success_resets_attempts(app, client):
    register_user(app)

    # Login first
    client.post(
        "/login",
        data={"username": "testuser", "password": "secret123"},
        follow_redirects=True,
    )

    # Prepare session with a deterministic target number
    with client.session_transaction() as session:
        session["target_number"] = 42
        session["attempts"] = 0

    response = client.post("/game", data={"guess": "42"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Treffer!" in response.data
    assert b"1 Versuche" in response.data
    assert b"Test Tester" in response.data

    with client.session_transaction() as session:
        assert session.get("attempts") == 0
        assert session.get("target_number") is not None
