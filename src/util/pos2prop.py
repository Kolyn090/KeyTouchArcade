from typing import Tuple
from src.util.screen_getter import Screen_Getter


def pos2prop(window, position: Tuple[int, int]) -> Tuple[float, float]:
    screen_getter = Screen_Getter()
    chosen_region = screen_getter.get_cropped_window_region(window)
    x = chosen_region[0]
    y = chosen_region[1]
    height = chosen_region[2]
    width = chosen_region[3]
    position_in_window = [
        position[0] - x,
        position[1] - y
    ]
    return (
        position_in_window[0] / width,
        position_in_window[1] / height)
