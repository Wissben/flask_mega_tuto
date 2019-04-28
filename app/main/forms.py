from random import randrange

from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy.sql.functions import current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Save changes')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and current_user.username != user.username:
            suggestion = username.data + '_' + str(randrange(0, 9999))
            raise ValidationError('The name {} is already taken, try {}'.format(username.data, suggestion))


class PostForm(FlaskForm):
    post = TextAreaField('Post', validators=[Length(min=0, max=140)])
    submit = SubmitField()
