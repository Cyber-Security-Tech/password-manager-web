from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from app import db, bcrypt
from app.models import User, VaultEntry
from app.forms import LoginForm, RegistrationForm, VaultEntryForm, EditVaultEntryForm
from app.utils import encrypt_password, decrypt_password

bp = Blueprint('main', __name__)

# Home route redirects authenticated users to dashboard
@bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

# --- User Login ---
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

# --- User Registration ---
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

# --- Dashboard: View & Add Entries ---
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

    # Fetch and decrypt all current user's entries
    entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
    decrypted_entries = [{
        'id': e.id,
        'website': e.website,
        'login_username': e.login_username,
        'password': decrypt_password(e.password_encrypted)
    } for e in entries]

    return render_template('dashboard.html', form=form, entries=decrypted_entries)

# --- User Logout ---
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# --- Delete Vault Entry ---
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

# --- Edit Vault Entry ---
@bp.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = VaultEntry.query.get_or_404(entry_id)
    if entry.owner != current_user:
        flash("You are not authorized to edit this entry.", "danger")
        return redirect(url_for('main.dashboard'))

    form = EditVaultEntryForm()

    if form.validate_on_submit():
        entry.website = form.website.data
        entry.login_username = form.login_username.data
        if form.password.data:  # Only update if password is provided
            entry.password_encrypted = encrypt_password(form.password.data)
        db.session.commit()
        flash("Entry updated successfully.", "success")
        return redirect(url_for('main.dashboard'))

    if request.method == 'GET':
        form.website.data = entry.website
        form.login_username.data = entry.login_username

    return render_template('edit_entry.html', form=form, entry=entry)
