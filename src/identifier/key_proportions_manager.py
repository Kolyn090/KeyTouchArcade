import json
from src.read.read_system_config import file_path


class Key_Proportions_Manager:
    def __init__(self):
        with open(file_path, 'r') as file:
            self._data = json.load(file)

    def get_key_proportions(self) -> dict[str, list]:
        return self._data["system"]["key-proportions"]

    def save_key_proportions(self, new_key_proportions: dict[str, list]):
        self._data["system"]["key-proportions"] = new_key_proportions
        with open(file_path, 'w') as file:
            json.dump(self._data, file, indent=4)


if __name__ == '__main__':
    kpm = Key_Proportions_Manager()
