import os
import sys
import inspect

"""
# Для корректного подключения файлов из /src/.
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
src_path = os.path.join(parent_dir, "src")
sys.path.insert(0, src_path)
"""


from main import DatabaseConnector
from main import db


def test_get_event_list():
    event_list = DatabaseConnector(db).get_event_list()
    print(type(event_list))
    assert isinstance(event_list, list) and len(event_list) == 3

