import pytest
from flask.testing import FlaskClient
from app import create_app, db
from app.models import User, VaultEntry


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "testsecret"
    })
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_full_user_flow(client: FlaskClient):
    # ✅ Register
    response = client.post("/register", data={
        "username": "testuser",
        "password": "Test1234!",
        "confirm_password": "Test1234!"
    }, follow_redirects=True)
    assert b"Account created!" in response.data

    # ✅ Login
    response = client.post("/login", data={
        "username": "testuser",
        "password": "Test1234!"
    }, follow_redirects=True)
    assert b"Login successful!" in response.data
    assert b"Dashboard" in response.data or b"Welcome, testuser" in response.data

    # ✅ Add a vault entry
    response = client.post("/dashboard", data={
        "website": "example.com",
        "login_username": "user@example.com",
        "password": "MySecretPass123!",
        "submit": True
    }, follow_redirects=True)
    assert b"Password saved!" in response.data

    # ✅ View dashboard and assert the saved entry is shown
    response = client.get("/dashboard", follow_redirects=True)
    assert b"example.com" in response.data
    assert b"user@example.com" in response.data


# ❌ Login with wrong password
def test_login_invalid_password(client: FlaskClient):
    # Create user manually
    client.post("/register", data={
        "username": "testuser",
        "password": "CorrectPass1!",
        "confirm_password": "CorrectPass1!"
    }, follow_redirects=True)

    response = client.post("/login", data={
        "username": "testuser",
        "password": "WrongPassword"
    }, follow_redirects=True)
    assert b"Invalid username or password" in response.data


# ❌ Registration with mismatched passwords
def test_register_mismatched_passwords(client: FlaskClient):
    response = client.post("/register", data={
        "username": "newuser",
        "password": "SomePassword!",
        "confirm_password": "MismatchPassword"
    }, follow_redirects=True)
    assert b"Passwords must match" in response.data


# ❌ Add vault entry without logging in
def test_unauthorized_entry_addition(client: FlaskClient):
    response = client.post("/dashboard", data={
        "website": "unauthorized.com",
        "login_username": "nope@nowhere.com",
        "password": "ShouldNotSave"
    }, follow_redirects=True)
    assert b"Please log in to access this page." in response.data
