import json
from src.read.read_system_config import file_path


class Key_Proportions_Manager:
    def __init__(self):
        with open(file_path, 'r') as file:
            self._data = json.load(file)

    def get_key_proportions(self) -> dict[str, list]:
        return self._data["system"]["key-proportions"]


if __name__ == '__main__':
    kpm = Key_Proportions_Manager()
