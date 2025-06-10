from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        label='Username:',
        validators=[Length(min=2, max=30), DataRequired()],
        filters=[lambda x: x.strip() if x else x]
    )
    email_address = StringField(
        label='Email Address:',
        validators=[Email(), DataRequired()],
        filters=[lambda x: x.strip() if x else x]
    )
    password1 = PasswordField(label='Password:', validators=[Length(min=5), DataRequired()])
    password2 = PasswordField(
        label='Confirm Password:',
        validators=[EqualTo('password1', message='Both passwords must match!'), DataRequired()]
    )
    submit = SubmitField(label='Create Account')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')


class ForgotPasswordForm(FlaskForm):
    email = StringField(label='Email Address', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(label='New Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password1', message="Passwords must match.")])
    submit = SubmitField(label='Reset Password')
