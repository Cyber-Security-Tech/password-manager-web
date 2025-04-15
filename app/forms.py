from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional


# Login form for user authentication
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Registration form for creating a new user
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')


# Vault entry form for adding new credentials
class VaultEntryForm(FlaskForm):
    website = StringField('Website', validators=[DataRequired()])
    login_username = StringField('Login Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Save Password')


# Vault entry form for editing credentials
class EditVaultEntryForm(FlaskForm):
    website = StringField('Website', validators=[DataRequired()])
    login_username = StringField('Login Username', validators=[DataRequired()])
    password = PasswordField('New Password (leave blank to keep current)', validators=[Optional()])
    submit = SubmitField('Update Entry')
