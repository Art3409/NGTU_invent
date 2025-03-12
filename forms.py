from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User  # Импортируем модель User

class RoomForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')

class ItemForm(FlaskForm):
    type = SelectField('Тип', choices=[
        ('внутрянка ПК', 'внутрянка ПК'),
        ('проводка', 'проводка'),
        ('техника и зап части', 'техника и зап части'),
        ('крепеж', 'крепеж'),
        ('средства гигиены лекарства и кухня', 'средства гигиены лекарства и кухня'),
        ('прочее', 'прочее')
    ], validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired()])
    status = SelectField('Статус', choices=[
        ('на месте', 'на месте'),
        ('взята на время', 'взята на время'),
        ('отдана в использование', 'отдана в использование')
    ], validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    role = SelectField('Роль', choices=[('user', 'Пользователь'), ('admin', 'Администратор')], default='user')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято.')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])