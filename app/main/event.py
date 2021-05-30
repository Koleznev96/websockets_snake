import datetime as dt


class Event:
    def __init__(self, name: str, organizer: str, type_game: str, mode_game: str,
                 run_date: dt.datetime, max_count_users: int, current_count_users: int,
                 duration: dt.time, record_avail: bool, broadcast_avail: bool):
        self.__name = name
        self.__organizer = organizer
        self.__type_game = type_game
        self.__mode_game = mode_game
        self.__max_count_users = max_count_users
        self.__current_count_users = current_count_users
        self.__run_date = run_date
        self.__duration = duration
        self.__record_avail = record_avail
        self.__broadcast_avail = broadcast_avail

    def get_name(self):
        return self.__name

    def get_organizer(self):
        return self.__organizer

    def get_type_game(self):
        return self.__type_game

    def get_mode_game(self):
        return self.__mode_game

    def get_max_count_users(self):
        return self.__max_count_users

    def get_current_count_users(self):
        return self.__current_count_users

    def get_run_date(self):
        return self.__run_date

    def get_duration(self):
        return self.__duration

    def get_record_avail(self):
        return self.__record_avail

    def get_broadcast_avail(self):
        return self.__broadcast_avail
