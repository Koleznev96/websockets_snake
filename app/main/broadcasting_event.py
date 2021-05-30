from app.main import game_modules
from typing import List
import datetime as dt
from app.main.event_member import EventMember


class BroadcastingEvent:
    def __init__(self, room_name: str, type_game: str, record_avail: bool,
                 run_date: dt.datetime, duration: dt.time, event_members: List[EventMember]):
        self.__room_name = room_name
        self.__record_avail = record_avail
        self.__run_date_broadcast = dt.datetime(
            run_date.year, run_date.month, run_date.day,
            run_date.hour + duration.hour, run_date.minute + duration.minute
        )
        self.__game = None

        if type_game == "snake":
            self.__game = game_modules.GameSnake(room_name=room_name,
                                                 event_members=event_members)

    def get_room_name(self):
        return self.__room_name

    def get_game(self):
        return self.__game

    def get_record_avail(self):
        return self.__record_avail

    def get_run_date_broadcast(self):
        return self.__run_date_broadcast
