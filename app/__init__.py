import sys
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "__login"


def create_app(config_name: str = "default") -> Flask:
    """
    Фабричная функция приложения.
    Создает настраиваемый экземпляр Flask(), т.е. нашего приложения.

    :param config_name: Название конфигурации.
    :return: Возвращает настроенный экземпляр приложения.
    """

    # Инициализируем наше приложение и загружаем конфигурацию.
    app = Flask(__name__,
                template_folder=sys.path[0] + "/app/templates/",
                static_folder=sys.path[0] + "/app/static/")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # Создаем глобальный контекст этого приложения, чтобы
    # база данных db могла работать без явного указания контекста.
    app.app_context().push()

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # Из-за вызова init_app app и db не будут связаны одним контекстом.
    # Для этого я вызвал app.app_context().push().
    # Сделано это, по словам разработчиков, из-за того, что такой подход
    # используется, когда мы создаем не одно, а несколько приложений.
    db.init_app(app)
    login_manager.init_app(app)

    return app
