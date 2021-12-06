from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from apps.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This user is existed. Please change username !')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Hey! This email is taken. Please change the email!')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class InforForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = StringField('Gender', validators=[DataRequired(), Length(min=4, max=10)])
    birthday = DateField('Birthday',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This user is existed. Please change username !')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Hey! This email is taken. Please change the email!')


class SellerForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    image_file = StringField('ImageFile', validators=[DataRequired()])
    photo = FileField(u'图片上传', validators=[
        FileAllowed(['jpg', 'png'], '只接收.jpg和.png格式的图片')
    ])
    submit = SubmitField('Save')


class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    photo = FileField(u'图片上传', validators=[
        FileAllowed(['jpg', 'png'], '只接收.jpg和.png格式的图片')
    ])
    submit = SubmitField('Upload')


