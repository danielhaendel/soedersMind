import pytest

from src import create_app


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
