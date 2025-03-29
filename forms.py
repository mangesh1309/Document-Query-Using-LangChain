from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(message="First name is required.")])
    last_name = StringField("Last Name", validators=[DataRequired(message="Last name is required.")])
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password is required."), Length(min=6, message="Password must be at least 6 characters.")])
    submit = SubmitField("Sign Up")

class LogInForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")])
    password = PasswordField("Password", validators=[DataRequired(message="Password is required."), Length(min=6, message="Password must be at least 6 characters.")])
    submit = SubmitField("Log In")