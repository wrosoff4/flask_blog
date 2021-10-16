from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import \
    BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import \
    DataRequired, Email, EqualTo, Length, ValidationError

from flask_blog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(),
                                       Length(min=2, max=20)])
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('password',
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):  # noqa
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken, try another one.')

    def validate_email(self, email):  # noqa
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with that email has already been registered.')


class LoginForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired()])
    password = PasswordField('password',
                             validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Stay logged in')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('username',
                           validators=[DataRequired(),
                                       Length(min=2, max=20)])
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture',
                        validators=[FileAllowed(['jpg', 'png'], 'Invalid File Type')])
    submit = SubmitField('Update')

    def validate_username(self, username):  # noqa
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username taken, try another one.')

    def validate_email(self, email):  # noqa
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with that email has already been registered.')


class RequestResetForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):  # noqa
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account associate with that email. Try creating an account')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('password',
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Reset Password')
