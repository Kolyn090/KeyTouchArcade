import tomllib
from typing import Tuple
from src.util.screen_getter import Screen_Getter
from src.read.read_user_config import file_path


def prop2pos(window, prop: Tuple[float, float]) -> Tuple[int, int]:
    x = window.left
    y = window.top
    width = window.width
    height = window.height
    return int(x + width * prop[0]), int(y + height * prop[1])

if __name__ == "__main__":
    with open(file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    pr = (0.47081218274111675, 0.4894957983193277)
    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])
    print(prop2pos(chosen_window, pr))
