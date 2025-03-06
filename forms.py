from xml.dom import ValidationErr

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from sqlalchemy import Boolean
from wtforms.fields.simple import StringField, PasswordField, SubmitField, FileField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FileField  # Добавлен SelectField
from wtforms.validators import DataRequired, EqualTo

from .models.user import User


class RegistrationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired(), Length(min = 2, max = 64)])
    login =  StringField('Логин', validators=[DataRequired(), Length(min = 5, max = 64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Загрузите фото', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Зарегистрироваться')
    submit_l = SubmitField('Войти')


    def validate_login(self, login):
        user = User.query.filter_by(login = login.data).first()
        if user:
            raise ValidationError('Данное имя пользователя уже занято, выберите другое')


class LoginForm(FlaskForm):
    login =  StringField('Логин', validators=[DataRequired(), Length(min = 5, max = 64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class ProfileForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired(), Length(min=5, max=64)])
    avatar = FileField('Аватар')  # Поле для загрузки файла
    submit = SubmitField('Сохранить изменения')


class EmployeeForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])

    # Добавляем SelectField с выбором "Кладовщик" или "Водитель"
    position = SelectField('Должность', choices=[('Кладовщик', 'Кладовщик'), ('Водитель', 'Водитель')],
                           validators=[DataRequired()])

    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])

    avatar = FileField('Фото')
    submit = SubmitField('Зарегистрировать')