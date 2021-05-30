import random
import json
import copy
from importlib import import_module
from app.main.game_interface import GameInterface
from app.main.event_member import EventMember
from typing import List


class GameSnake(GameInterface):
    """Модуль игры змейка"""
    def __init__(self, room_name: str, event_members: List[EventMember]):
        self.__room_name = room_name

        list_users_file = []
        for member in event_members:
            list_users_file.append({"user": member.get_name(),
                                    "file": member.get_name()})

        self.__height_field = 30
        self.__width_field = 30

        self.__users = []

        self.__playing_field = []

        # Заполняем массив стенок
        self.__walls = []
        for y in range(self.__height_field):
            for x in range(self.__width_field):
                if x == 0 or y == 0 or x == self.__width_field - 1 or y == self.__height_field - 1:
                    self.__walls.append({"x": x, "y": y})

        # Создаем точки респауна
        self.__respawn_snakes = []
        for y in range(self.__height_field):
            for x in range(self.__width_field):
                if not ({"x": x, "y": y} in self.__walls):
                    self.__respawn_snakes.append({"x": x, "y": y})

        random.shuffle(self.__respawn_snakes)

        counter = 0
        for user in list_users_file:
            self.__users.append(
                Snake(user["user"], user["file"], [self.__respawn_snakes[counter]])
            )
            counter += 1

        self.__food = self._creation_food(self.__height_field, self.__width_field,  self.__walls, self.__users)

        self.__current_cords = ""
        self.__history = []

    def delete_history(self):
        self.__history = None

    def get_history(self):
        return self.__history

    def calculation_game(self):
        for _ in range(1000):
            # Собираем поле в двухмерный массив
            self.__playing_field = self._creature_playing_field(
                self.__height_field,
                self.__width_field,
                self.__users,
                self.__food)

            for user in self.__users:
                """
                Изменяем поле, для алгоритма пользователя
                0 - пусто
                1 - препятствие
                2 - еда
                3 - голова змейки
                4 - тело змейки
                """
                playing_field_user = copy.deepcopy(self.__playing_field)
                for y in range(self.__height_field):
                    for x in range(self.__width_field):
                        if playing_field_user[y][x] == {"type": "empty"}:
                            playing_field_user[y][x] = 0
                        elif playing_field_user[y][x] == {"type": "apple"}:
                            playing_field_user[y][x] = 2
                        elif playing_field_user[y][x] == {"type": "snake_head", "user": user.get_user()}:
                            playing_field_user[y][x] = 3
                        elif playing_field_user[y][x] == {"type": "snake_body", "user": user.get_user()}:
                            playing_field_user[y][x] = 4
                        else:
                            playing_field_user[y][x] = 1

                # запускаем алгоритм пользователя
                try:
                    module = __import__(user.get_file())
                    direction = module.user_algorithm(playing_field_user)
                except:
                    # При выволнении алгоритма поользователя, появилась ошибка
                    self.__users.remove(user)
                    continue

                new_head = {
                    "x": user.get_snake()[0]["x"],
                    "y": user.get_snake()[0]["y"]
                }

                # Изменяем координаты головы, т.е. двигаем змейку.
                if direction == "left":
                    new_head["x"] -= 1
                elif direction == "right":
                    new_head["x"] += 1
                elif direction == "up":
                    new_head["y"] -= 1
                elif direction == "down":
                    new_head["y"] += 1
                else:
                    # Алгоритм пользователя вернул не верный ответ
                    self.__users.remove(user)
                    continue

                # Проверка не врезалась ли змейка в стену
                for el in self.__walls:
                    if new_head["x"] == el["x"] and new_head["y"] == el["y"]:
                        self.__users.remove(user)

                # Добавляем новую голову в начало.
                user.add_new_head(new_head)

                # Если змейка съела еду.
                if user.get_snake()[0]["x"] == self.__food["x"] and user.get_snake()[0]["y"] == self.__food["y"]:
                    user.change_score()
                    self.__food = {
                        "x": -1,
                        "y": -1
                    }
                else:
                    user.remove_last_element_snake()

            if self.__food == {"x": -1, "y": -1}:
                self.__food = self._creation_food(self.__height_field, self.__width_field, self.__walls, self.__users)

            data_users = []
            for data in self.__users:
                data_users.append(data.get_user_score())

            # Подготавливаем данные для передачи на клиент
            shipping_customer = {'playing_field': self.__playing_field,
                                 'data_users': data_users}

            # Преобразуем обьект в строку
            shipping_customer_text = json.dumps(shipping_customer)

            self.__current_cords = shipping_customer_text
            self.__history.append(shipping_customer_text)

            for user in self.__users:
                # Проверяем не врезалась ли змейка в себя
                for i in range(1, len(user.get_snake())):
                    if user.get_snake()[0] == user.get_snake()[i]:
                        self.__users.remove(user)

                for user_next in self.__users:
                    if user_next.get_snake() != user.get_snake():
                        # Проверяем не врезалась ли змейка в чужую голову
                        if user_next.get_snake()[0] == user.get_snake()[0]:
                            self.__users.remove(user_next)
                            self.__users.remove(user)
                        else:
                            for k in range(1, len(user_next.get_snake())):
                                # Проверяем не врезалась ли змейка в тело друго змейки
                                if user.get_snake()[0] == user_next.get_snake()[k]:
                                    self.__users.remove(user)

    @staticmethod
    def _creature_playing_field(height, width, users, food):
        """Создание двухмерного массива поля"""
        playing_field = []
        for y in range(height):
            playing_field.append([])
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    playing_field[y].append({"type": "let"})
                else:
                    playing_field[y].append({"type": "empty"})

        playing_field[food["y"]][food["x"]] = {"type": "apple"}

        for user in users:
            counter = 0
            for snake in user.get_snake():
                if counter == 0:
                    playing_field[snake["y"]][snake["x"]] = {"type": "snake_head", "user": user.get_user()}
                else:
                    playing_field[snake["y"]][snake["x"]] = {"type": "snake_body", "user": user.get_user()}
                counter += 1

        return playing_field

    @staticmethod
    def _creation_food(height, width, walls, users):
        """Создание еды"""
        occupied_fields = []

        # Добавляем все занятые поля стенками
        occupied_fields += walls

        # Добавляем все занятые поля змейками
        for user in users:
            occupied_fields += user.get_snake()

        empty_fields = []
        for y in range(height):
            for x in range(width):
                if not ({"x": x, "y": y} in occupied_fields):
                    empty_fields.append({"x": x, "y": y})

        random.shuffle(empty_fields)
        food = empty_fields[0]

        return food


class Snake:
    """Класс змейки пользователя"""
    def __init__(self, user, file, snake):
        self.__user = user
        self.__file = file
        self.__snake = snake
        self.__score = 0

    def change_score(self):
        self.__score += 1

    def remove_last_element_snake(self):
        self.__snake.pop()

    def add_new_head(self, new_head):
        self.__snake.insert(0, new_head)

    def get_user(self):
        return self.__user

    def get_file(self):
        return self.__file

    def get_snake(self):
        return self.__snake

    def get_score(self):
        return self.__score

    def get_date(self):
        """Получение всех данных"""
        return {
            "user": self.__user,
            "score": self.__score,
            "snake": self.__snake,
            "file": self.__file
        }

    def get_user_score(self):
        return {
            "user": self.__user,
            "score": self.__score
        }
