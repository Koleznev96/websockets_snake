from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo


class AuthForm(Form):
    name = StringField(label="Имя", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(label="Пароль", validators=[DataRequired()])
    remember_me = BooleanField(label="Запомнить меня")
    submit_btn = SubmitField(label="Войти")


class RegistrationForm(Form):
    name = StringField(label="Имя", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(label="Пароль",
                             validators=[DataRequired(),
                                         EqualTo("confirm_password", message="Пароли должны совпадать")])
    confirm_password = PasswordField(label="Повторите пароль", validators=[DataRequired()])
    submit_btn = SubmitField(label="Регистрация")


class CreateEventForm(Form):
    name = StringField(label="Название", validators=[DataRequired(), Length(1, 64)])
    organizer = StringField(label="Организатор", validators=[DataRequired(), Length(1, 64)])
    type_game = StringField(label="Игра", validators=[DataRequired(), Length(1, 64)])
    mode_game = StringField(label="Режим", validators=[DataRequired(), Length(1, 64)])
    max_count_users = IntegerField(label="Участники", validators=[DataRequired()])
    date = DateField(label="Дата", validators=[DataRequired()])
    time = TimeField(label="Время", validators=[DataRequired()])
    duration = TimeField(label="Длительность", validators=[DataRequired()])
    record_avail = BooleanField(label="Запись")
    broadcast_avail = BooleanField(label="Трансляция")
    submit_btn = SubmitField(label="Создать")
