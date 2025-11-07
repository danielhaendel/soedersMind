import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src import create_app
from src.services.users import create_user


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": str(database_path),
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def register_user(app):
    def _register(
        *,
        username: str = "testuser",
        password: str = "secret123",
        first_name: str = "Test",
        last_name: str = "User",
        email: str = "test@example.com",
    ):
        with app.app_context():
            user = create_user(username, password, first_name, last_name, email)
        return user, password

    return _register


@pytest.fixture
def auth_client(client, register_user):
    user, password = register_user()
    response = client.post(
        "/login",
        data={"username": user.username, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client, user
