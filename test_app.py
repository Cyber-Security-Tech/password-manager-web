import pytest
from app import create_app, db
from app.models import User, VaultEntry
from flask import session

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # use in-memory DB for testing
    app.config['WTF_CSRF_ENABLED'] = False  # disable CSRF for test
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_full_user_flow(client):
    # Register user
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'Test1234!',
        'confirm_password': 'Test1234!'
    }, follow_redirects=True)
    assert b'Account created! You can now log in.' in response.data

    # Login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'Test1234!'
    }, follow_redirects=True)
    assert b'Login successful!' in response.data
    assert b'Welcome, testuser' in response.data

    # Add vault entry
    response = client.post('/dashboard', data={
        'website': 'github.com',
        'login_username': 'user@example.com',
        'password': 'MySecurePass123!',
        'submit': True
    }, follow_redirects=True)
    assert b'Password saved!' in response.data
    assert b'github.com' in response.data
    assert b'user@example.com' in response.data

    # Delete the vault entry
    with client.session_transaction() as sess:
        user = User.query.filter_by(username="testuser").first()
        entry = VaultEntry.query.filter_by(user_id=user.id).first()
        entry_id = entry.id

    response = client.post(f'/delete/{entry_id}', follow_redirects=True)
    assert b'Entry deleted successfully.' in response.data
    assert b'github.com' not in response.data

    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out.' in response.data
