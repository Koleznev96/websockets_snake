import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "a really really really really long secret key"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = "[Flasky]"
    FLASKY_MAIL_SENDER = "Flasky Admin <flasky@example.com>"
    FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:DOKTOR_ZLO@localhost:5432/postgres"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:DOKTOR_ZLO@127.0.0.1:5432/postgres"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:DOKTOR_ZLO@127.0.0.1:5432/postgres"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
