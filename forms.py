from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User, Room

class RoomForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')

class ItemForm(FlaskForm):
    type = SelectField('Тип', choices=[
        ('ПК и комплектующие', 'ПК и комплектующие'),
        ('Провода', 'Провода'),
        ('Техника и комплектующие', 'Техника и комплектующие'),
        ('Крепеж', 'Крепеж'),
        ('Приборы', 'Приборы'),
        ('Инструмент', 'Инструмент'),
        ('Прочее', 'Прочее')
    ], validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired()])
    status = SelectField('Статус', choices=[
        ('В ИВЦ', 'В ИВЦ'),
        ('Взято на время', 'Взято на время'),
        ('Отдано в использование', 'Отдано в использование')
    ], validators=[DataRequired()])
    room_id = SelectField('Аудитория', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.room_id.choices = [(r.id, r.name) for r in Room.query.order_by('name')]

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