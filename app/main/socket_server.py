import time
import os
import sys
from datetime import datetime
from typing import Dict
from threading import Lock
from flask_socketio import SocketIO
from flask_socketio import join_room
from flask_socketio import leave_room
from apscheduler.schedulers.background import BackgroundScheduler
from app.main.database_connector import DatabaseConnector
from app.main.broadcasting_event import BroadcastingEvent


class SocketServer:
    """
    Класс сокетного сервера.
    Обрабатывает все запросе пользователей к серверу через сокеты.
    Обеспечивает трансляцию игр пользователям.
    """

    def __init__(self, socket: SocketIO, db_connector: DatabaseConnector):
        """
        Инициализатор класса.
        :param socket: Серверный сокет для общения с клиентами.
        """

        self.__db_connector = db_connector
        self.__socket_io = socket

        # Запускаем обработчики.
        self.connect_client = self.__socket_io.on("connect")(self.__connect_client)
        self.disconnect_client = self.__socket_io.on("disconnect")(self.__disconnect_client)
        self.client_join_room = self.__socket_io.on("join")(self.__client_join_room)
        self.client_leave_room = self.__socket_io.on("leave")(self.__client_leave_room)

        self.__list_rooms = []

        # Запуск планировщика.
        self.__scheduler = BackgroundScheduler()
        self.__update_tasks()
        # Говорим планировщику раз в день обновлять список событий.
        self.__scheduler.add_job(self.__update_tasks, "interval", days=1)
        self.__scheduler.start()

    def __del__(self):
        self.__scheduler.remove_all_jobs()
        self.__scheduler.shutdown()

    def __update_tasks(self):
        """Обновление задач планировщика"""
        # Добавляем новые события в планировщик и создаем их комнаты (папки).
        events = self.__db_connector.get_events_to_broadcast()
        for event in events:
            self.__scheduler.add_job(self.__room_thread, "date",
                                     run_date=event.get_run_date_broadcast(),
                                     args=[event])
            try:
                os.mkdir(sys.path[0] + f"/app/rooms/{event.get_room_name()}")
            except OSError:
                print("Такая комната уже есть")

    def __room_thread(self, event: BroadcastingEvent):
        """
        Метод запуска комнаты в потоке.
        :param event: Обрабатываемое событие в потоке.
        :return:
        """
        with Lock():
            self.__list_rooms.append(event.get_room_name())

        # Скорость трансляции.
        broadcast_delay = 0.4
        # Рассчитываем всю игру.
        # После этого у нас есть готовая история игры в game.
        event.get_game().calculation_game()

        # Транслируем историю пошагово.
        for game_step in event.get_game().get_history():
            self.__socket_io.emit("message", game_step, room=event.get_room_name())
            time.sleep(broadcast_delay)

        # Если записи не должно быть - удаляем.
        if not event.get_record_avail():
            event.get_game().delete_history()
        else:
            # TODO: Если запись есть, сохраняем.
            pass

        # Удаляем само событие из БД.
        self.__db_connector.delete_event(event_name=event.get_room_name())

        # Используем мьютекс для синхронизации потоков.
        with Lock():
            # По окончании трансляции удаляем комнату и поток.
            for i, room in enumerate(self.__list_rooms):
                if room == event.get_room_name():
                    self.__list_rooms.pop(i)
                    print(f"{room} deleted")
                    break

    @staticmethod
    def __connect_client():
        """Подключение клиента"""
        print("Client connected")

    @staticmethod
    def __disconnect_client():
        """Отключение клиента"""
        print("Client disconnected")

    def __client_join_room(self, data: Dict[str, str]):
        """
        Метод подключения клиента в комнату.
        :param data: Данные пользователя. Приходят с клиента.
        :return:
        """
        username = data["username"]
        name_room = data["room"]

        if name_room not in self.__list_rooms:
            print(f"{name_room} not started")
        else:
            join_room(name_room)
            print(f"{username}'s connected to {name_room}")

    def __client_leave_room(self, data: Dict):
        """
        Метод отключения клиента от комнаты.
        :param data: Данные пользователя. Приходят с клиента.
        :return:
        """
        username = data["username"]
        name_room = data["room"]

        if name_room not in self.__list_rooms:
            print(f"{name_room} not exist")
        else:
            leave_room(name_room)
            print(f"{username}'s disconnected from {name_room}")
