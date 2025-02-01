from typing import Tuple
from src.util.screen_getter import Screen_Getter


def prop2pos(window, proportion: Tuple[float, float]) -> Tuple[int, int]:
    screen_getter = Screen_Getter()
    chosen_region = screen_getter.get_cropped_window_region(window)
    x = chosen_region[0]
    y = chosen_region[1]
    height = chosen_region[2]
    width = chosen_region[3]
    return int(x + width * proportion[0]), int(y + height * proportion[1])
