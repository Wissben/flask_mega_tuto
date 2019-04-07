from flask_wtf import FlaskForm
from sqlalchemy.sql.functions import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User
from random import randrange
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me ?', default="checked")
    submit = SubmitField('Submit')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    password_verification = StringField('Password verficiation', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            suggestion = username.data + '_' + str(randrange(0, 9999))
            raise ValidationError('The name {} is already taken, try {}'.format(username.data, suggestion))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The mail already exists')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)]    )
    submit = SubmitField('Save changes')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not  None and current_user.username != user.username:
            suggestion = username.data + '_' + str( randrange(0,9999))
            raise ValidationError('The name {} is already taken, try {}'.format(username.data,suggestion))
