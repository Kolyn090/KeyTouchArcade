import cv2
import platform
if platform.platform().startswith('Win'):
    import pygetwindow as gw
import numpy as np
from PIL import Image, ImageGrab
from src.window_prop import get_perfect_window_region


# This function will look for a window with a specific title
def get_window_with_title(title):
    def get_window_list_win():
        return gw.getAllWindows()

    def get_win_window():
        for window in get_window_list_win():
            if window.title.startswith(title):
                return window
        return None

    return get_win_window()


def get_screenshot_of_chosen_window(window) -> Image.Image:
    """
    Assuming using BlueStacks emulator.
    Assuming ads widget exists but is hidden.
    Returns a screenshot without ads widget and topbar.
    :param window: BlueStacks window
    :return: the screenshot of window
    """
    window_region = get_perfect_window_region(window)
    x = window_region[1]
    y = window_region[0]
    h = window_region[3]
    w = window_region[2]
    return ImageGrab.grab(bbox=(x, y, w, h))


def get_screenshot_of_chosen_region(window, region) -> Image.Image:
    window_region = get_perfect_window_region(window)
    x = window_region[1]
    y = window_region[0]

    x = x + region[0]
    y = y + region[1]
    w = region[2] - region[0]
    h = region[3] - region[1]

    return ImageGrab.grab(bbox=(x, y, x + w, y + h))


def get_screenshot_of_chosen_region_cv2(window, region) -> np.ndarray:
    window_region = get_perfect_window_region(window)
    x = window_region[1]
    y = window_region[0]

    x = x + region[0]
    y = y + region[1]
    w = region[2] - region[0]
    h = region[3] - region[1]

    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img_cv = np.array(img)

    return cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
