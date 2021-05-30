from flask_login import UserMixin
from werkzeug import security


class User(UserMixin):
    def __init__(self, name: str, password: str,
                 role: str, hashing: bool = False):
        """
        Инициализатор класса.
        :param name: Имя пользователя.
        :param password: Пароль пользователя.
        :param role: Роль пользователя.
        :param hashing: Нужно ли хешировать пароль для этого объекта.
        """
        self.__name = name
        self.__password = security.generate_password_hash(password) if hashing else password
        self.__role = role

    def get_id(self):
        return self.__name

    def get_name(self):
        return self.__name

    def get_password(self):
        return self.__password

    def get_role(self):
        return self.__role

    def verify_password(self, password: str) -> bool:
        """
        Метод проверки хэша пароля с данным паролем.
        :param password: Пароль, который проверяется.
        :return: Возвращает True или False.
        """
        return security.check_password_hash(self.__password, password)
