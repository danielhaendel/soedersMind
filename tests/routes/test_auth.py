import pytest


def test_register_and_login_flow_via_routes(client):
    response = client.post(
        "/register",
        data={
            "username": "hero",
            "password": "geheim123",
            "confirm": "geheim123",
            "first_name": "Hero",
            "last_name": "Tester",
            "email": "hero@example.com",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registrierung erfolgreich" in response.data

    response = client.post(
        "/login",
        data={"username": "hero", "password": "geheim123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Eingeloggt als" in response.data
    assert b"Hero Tester" in response.data


@pytest.mark.parametrize(
    "form_data, expected_message",
    [
        (
            {
                "username": "",
                "password": "",
                "confirm": "",
                "first_name": "",
                "last_name": "",
                "email": "",
            },
            b"Bitte einen Benutzernamen und ein Passwort eingeben",
        ),
        (
            {
                "username": "profileless",
                "password": "pw123456",
                "confirm": "pw123456",
                "first_name": "",
                "last_name": "",
                "email": "",
            },
            b"Bitte Vorname, Nachname und E-Mail angeben",
        ),
        (
            {
                "username": "mismatch",
                "password": "pw123456",
                "confirm": "pw654321",
                "first_name": "Miss",
                "last_name": "Match",
                "email": "miss@example.com",
            },
            "Passw\u00f6rter stimmen nicht \u00fcberein".encode("utf-8"),
        ),
    ],
)
def test_register_validations_trigger_expected_flash_messages(client, form_data, expected_message):
    response = client.post("/register", data=form_data, follow_redirects=True)
    assert expected_message in response.data


def test_register_rejects_duplicate_usernames(client, register_user):
    register_user(username="dupe", email="dupe@example.com")

    response = client.post(
        "/register",
        data={
            "username": "dupe",
            "password": "newpass123",
            "confirm": "newpass123",
            "first_name": "Dupe",
            "last_name": "Again",
            "email": "dupe2@example.com",
        },
        follow_redirects=True,
    )
    assert b"Benutzername ist bereits vergeben" in response.data


def test_login_with_invalid_credentials_shows_error(client, register_user):
    register_user(username="badlogin", password="pass123", email="bad@example.com")

    response = client.post(
        "/login",
        data={"username": "badlogin", "password": "falsch"},
        follow_redirects=True,
    )
    assert "Ung\u00fcltiger Benutzername oder Passwort".encode("utf-8") in response.data


def test_login_route_redirects_authenticated_users(auth_client):
    client, _ = auth_client
    response = client.get("/login")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_clears_session_and_redirects_to_login(auth_client):
    client, _ = auth_client

    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    with client.session_transaction() as session:
        assert "_user_id" not in session
