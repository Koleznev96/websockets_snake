import os
from app import create_app, db, login_manager
from flask_socketio import SocketIO
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# Импортируем наши классы для работы системы.
from app.main.socket_server import SocketServer
from app.main.web_server import WebServer
from app.main.database_connector import DatabaseConnector
#from app.models import *


# Создаем приложение и на его основе инициализируем необходимые классы.
app = create_app()
socket_io = SocketIO(app)
db_connector = DatabaseConnector(db=db, login_manager=login_manager)
web_server = WebServer(application=app, db_connector=db_connector,
                       login_manager=login_manager)
socket_server = SocketServer(socket=socket_io, db_connector=db_connector)


if __name__ == "__main__":
    socket_io.run(app)
