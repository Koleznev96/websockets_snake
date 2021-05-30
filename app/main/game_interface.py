from abc import ABC
from abc import abstractmethod


class GameInterface(ABC):
    @abstractmethod
    def delete_history(self):
        pass

    @abstractmethod
    def get_history(self):
        pass

    @abstractmethod
    def calculation_game(self):
        pass
