from typing import List
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.main.event import Event
from app.main.broadcasting_event import BroadcastingEvent
from app.main.user import User
from app.main.event_member import EventMember
from datetime import datetime


class DatabaseConnector:
    """
    Класс DatabaseConnector предоставляет удобный и жизненно
    необходимый функционал, удовлетворяющий всем запросам классов
    WebServer и SocketServer.
    """

    def __init__(self, db: SQLAlchemy, login_manager: LoginManager):
        """
        Инициализатор класса.
        :param db: Объект базы данных SQLAlchemy.
        :param login_manager: Объект логин менеджера для сохранения юзеров в сессии.
        """
        # Движок БД для запросов.
        self.__engine = db.engine
        self.__login_manager = login_manager

        # Метод необходим для менеджера входа пользователей.
        self.load_user = self.__login_manager.user_loader(self.__load_user)

    def __load_user(self, username: str) -> User:
        """
        Метод загрузки юзера с его данными.
        Сам метод приватный, но вызываем мы self.load_user, который
        вдобавок к этому методу снабжен декоратором user_loader из login_manager.
        :param username: Имя нужного юзера.
        :return: Возвращает объект типа User.
        """
        query_result = self.__engine.execute(
            f"SELECT * FROM users WHERE username='{username}';"
        )

        user = None
        for row in query_result:
            user = User(name=row.username,
                        password=row.password_hash,
                        role=row.role)
        return user

    def load_event(self, event_name) -> Event:
        """
        Метод загрузки события из БД.
        :param event_name: Название события.
        :return: Объект типа Event.
        """
        query_result = self.__engine.execute(
            f"SELECT * FROM events WHERE name='{event_name}';"
        )

        event = None
        for row in query_result:
            event = Event(name=row.name,
                          organizer=row.organizer,
                          type_game=row.type_game,
                          mode_game=row.mode_game,
                          current_count_users=row.current_count_users,
                          max_count_users=row.max_count_users,
                          run_date=row.run_date,
                          duration=row.duration,
                          record_avail=row.record_avail,
                          broadcast_avail=row.broadcast_avail)
        return event

    def validate_event(self, event_name: str) -> bool:
        """
        Метод валидации нового события по имени.
        :param event_name: Имя нового события.
        :return: True или False.
        """
        query_result = self.__engine.execute(
            f"SELECT name FROM events WHERE name='{event_name}';"
        )
        event_valid = True
        for row in query_result:
            event_valid = False
        return event_valid

    def register_event(self, event: Event):
        """
        Метод добавления нового события в БД.
        :param event: Ссылка на объект события.
        :return:
        """
        self.__engine.execute(
            f"INSERT INTO events (name, organizer, run_date, duration, type_game, "
            f"record_avail, broadcast_avail, max_count_users, current_count_users, mode_game) "
            f"VALUES ('{event.get_name()}', "
            f"'{event.get_organizer()}', "
            f"'{event.get_run_date()}', "
            f"'{event.get_duration()}', "
            f"'{event.get_type_game()}', "
            f"'{event.get_record_avail()}', "
            f"'{event.get_broadcast_avail()}', "
            f"{event.get_max_count_users()}, "
            f"{event.get_current_count_users()}, "
            f"'{event.get_mode_game()}');"
        )

    def delete_event(self, event_name: str):
        """
        Метод удаления события из БД.
        :param event_name: Название события.
        :return:
        """

        self.__engine.execute(
            f"DELETE FROM users_to_events WHERE event_name='{event_name}';"
            f"DELETE FROM events WHERE name='{event_name}';"
        )

    def validate_username(self, username: str) -> bool:
        """
        Метод валидации нового пользователя по имени.
        :param username: Имя нового юзера.
        :return: True или False.
        """
        query_result = self.__engine.execute(
            f"SELECT username FROM users WHERE username='{username}';"
        )
        user_valid = True
        for row in query_result:
            user_valid = False
        return user_valid

    def register_user(self, user: User):
        """
        Метод добавления нового юзера в БД. Регистарция.
        :param user: Ссылка на объект юзера.
        :return:
        """
        self.__engine.execute(
            f"INSERT INTO users (username, password_hash, role) "
            f"VALUES ('{user.get_name()}', "
            f"'{user.get_password()}', "
            f"'{user.get_role()}');"
        )

    def user_in_event(self, username: str, event_name: str) -> bool:
        """
        Метод валидации пользователя, который хочет зарегаться на событие.
        :param username: Имя юзера.
        :param event_name: Название события.
        :return: True или False.
        """
        query_result = self.__engine.execute(
            f"SELECT user_name FROM users_to_events "
            f"WHERE user_name='{username}' AND event_name='{event_name}';"
        )
        user_reg = False
        for row in query_result:
            user_reg = True
            break
        return user_reg

    def event_open_for_registration(self, event_name: str) -> bool:
        """
        Метод проверки возможности регистрации на данное событие.
        Проверяет наличие мест на событие и дату начала события.
        :param event_name: Название события.
        :return: True или False.
        """
        query_result = self.__engine.execute(
            f"SELECT run_date,current_count_users,max_count_users "
            f"FROM events WHERE name='{event_name}';"
        )
        event_open = True
        for row in query_result:
            if row.current_count_users + 1 > row.max_count_users \
                    or row.run_date <= datetime.now():
                event_open = False
                break
        return event_open

    def register_user_to_event(self, username: str, event_name: str):
        """
        Метод регистрации юзера на событие.
        :param username: Имя юзера.
        :param event_name: Название события.
        :return:
        """
        self.__engine.execute(
            f"INSERT INTO users_to_events (user_name, event_name)"
            f"VALUES ('{username}', '{event_name}');"
            f"UPDATE events SET current_count_users=current_count_users + 1 WHERE name='{event_name}';"
        )

    def unregister_user_from_event(self, username: str, event_name: str):
        """
        Метод удаления юзера из события.
        :param username: Имя юзера.
        :param event_name: Название события.
        :return:
        """
        self.__engine.execute(
            f"DELETE FROM users_to_events "
            f"WHERE user_name='{username}' AND event_name='{event_name}';"
            f"UPDATE events SET current_count_users=current_count_users - 1 "
            f"WHERE name='{event_name}';"
        )

    def get_all_events(self) -> List[Event]:
        """Метод получения всех событий"""
        query_result = self.__engine.execute("SELECT * FROM events;")
        events = []
        for row in query_result:
            new_event = Event(name=row.name,
                              organizer=row.organizer,
                              type_game=row.type_game,
                              mode_game=row.mode_game,
                              current_count_users=row.current_count_users,
                              max_count_users=row.max_count_users,
                              run_date=row.run_date,
                              duration=row.duration,
                              record_avail=row.record_avail,
                              broadcast_avail=row.broadcast_avail)
            events.append(new_event)
        return events

    def get_user_events(self, username: str) -> List[Event]:
        """
        Метод получения списка событий, на которые зареган юзер.
        :param username: Имя пользователя.
        :return: Список событий, на которые зареган юзер.
        """
        user_events = self.__engine.execute(
            f"SELECT event_name FROM users_to_events "
            f"WHERE user_name='{username}';"
        )
        result_events = []
        # По полученному имени события, на который зареган юзер,
        # получаем данные об этом событии и создаем объект Event.
        # Т.к. имя события уникально, запись будет только одна.
        for row in user_events:
            query_events = self.__engine.execute(
                f"SELECT * FROM events WHERE name='{row.event_name}';"
            )
            for event in query_events:
                new_event = Event(name=event.name,
                                  organizer=event.organizer,
                                  type_game=event.type_game,
                                  mode_game=event.mode_game,
                                  current_count_users=event.current_count_users,
                                  max_count_users=event.max_count_users,
                                  run_date=event.run_date,
                                  duration=event.duration,
                                  record_avail=event.record_avail,
                                  broadcast_avail=event.broadcast_avail)
                result_events.append(new_event)
        return result_events

    def get_events_to_broadcast(self) -> List[BroadcastingEvent]:
        """
        Метод получения списка событий, которые нужно добавить в планировщик.
        Добавляются события, до начала которых осталось меньше 1 дня.
        :return: Список событий для трансляции.
        """
        query_events = self.__engine.execute(
            f"SELECT name,type_game,record_avail,run_date,duration "
            f"FROM events WHERE DATE_PART('day', run_date::timestamp - '{datetime.now()}'::timestamp) <= 1;"
        )
        result_events = []
        for event in query_events:
            query_members = self.__engine.execute(
                f"SELECT user_name FROM users_to_events "
                f"WHERE event_name='{event.name}';"
            )
            members = []
            for member in query_members:
                new_member = EventMember(member_name=member.user_name)
                members.append(new_member)
            new_event = BroadcastingEvent(room_name=event.name,
                                          type_game=event.type_game,
                                          record_avail=event.record_avail,
                                          run_date=event.run_date,
                                          duration=event.duration,
                                          event_members=members)
            result_events.append(new_event)
        return result_events
