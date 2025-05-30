from . import db
from flask_login import UserMixin

# User model for authentication and ownership of vault entries
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # One-to-many: A user can have many vault entries
    vault_entries = db.relationship('VaultEntry', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# VaultEntry model for storing encrypted credentials
class VaultEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(255), nullable=False)
    login_username = db.Column(db.String(255), nullable=False)
    password_encrypted = db.Column(db.Text, nullable=False)

    # Foreign key linking this entry to the User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<VaultEntry {self.website} for {self.login_username}>'
