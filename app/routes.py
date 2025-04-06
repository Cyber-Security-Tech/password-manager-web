from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, VaultEntry
from app.forms import LoginForm, RegistrationForm, VaultEntryForm
from app.utils import encrypt_password, decrypt_password
from sqlalchemy.exc import IntegrityError

bp = Blueprint('main', __name__)


# Home → Login form
@bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    return render_template('login.html', form=form)


# Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)


# Register
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Account created! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'danger')

    return render_template('register.html', form=form)


# Dashboard
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = VaultEntryForm()

    if form.validate_on_submit():
        encrypted_pw = encrypt_password(form.password.data)
        new_entry = VaultEntry(
            website=form.website.data,
            login_username=form.login_username.data,
            password_encrypted=encrypted_pw,
            owner=current_user
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Password saved!', 'success')
        return redirect(url_for('main.dashboard'))

    entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
    decrypted_entries = []
    for entry in entries:
        decrypted_entries.append({
            'id': entry.id,
            'website': entry.website,
            'login_username': entry.login_username,
            'password': decrypt_password(entry.password_encrypted)
        })

    return render_template('dashboard.html', form=form, entries=decrypted_entries)


# Logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# Delete Vault Entry
@bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = VaultEntry.query.get_or_404(entry_id)
    if entry.owner != current_user:
        flash("You are not authorized to delete this entry.", "danger")
        return redirect(url_for('main.dashboard'))

    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for('main.dashboard'))
