from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length




class RegisterUserForm(FlaskForm):
    """Registration From for User"""

    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[Length(min=6)])
    image_url = StringField("(Optional) Image URL")
    location = StringField("Location")
    bio = TextAreaField("Your Bio")

class LoginForm(FlaskForm):
    """Login Form"""

    username = StringField("Username",validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])

class MessageForm(FlaskForm):
    """Form for adding/editing message"""

    text = TextAreaField("text", validators=[DataRequired()])