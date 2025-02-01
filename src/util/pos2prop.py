import tomllib
from typing import Tuple
from src.util.screen_getter import Screen_Getter
from src.read.read_user_config import file_path


def pos2prop(window, position: Tuple[int, int]) -> Tuple[float, float]:
    x = window.left
    y = window.top
    width = window.width
    height = window.height
    position_in_window = [
        position[0] - x,
        position[1] - y
    ]
    return (
        position_in_window[0] / width,
        position_in_window[1] / height)


if __name__ == "__main__":
    with open(file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    pos = (371, 233)
    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])
    print(pos2prop(chosen_window, pos))
