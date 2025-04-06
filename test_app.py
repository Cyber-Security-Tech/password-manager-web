import pytest
from flask import Flask
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
    # Register
    response = client.post("/register", data={
        "username": "testuser",
        "password": "Test1234!",
        "confirm_password": "Test1234!"
    }, follow_redirects=True)
    assert b"Account created!" in response.data

    # Login
    response = client.post("/login", data={
        "username": "testuser",
        "password": "Test1234!"
    }, follow_redirects=True)
    assert b"Login successful!" in response.data
    assert b"Dashboard" in response.data or b"Welcome, testuser" in response.data

    # Add a vault entry
    response = client.post("/dashboard", data={
        "website": "example.com",
        "login_username": "user@example.com",
        "password": "MySecretPass123!",
        "submit": True
    }, follow_redirects=True)
    assert b"Password saved!" in response.data
