import cv2
import tomllib
import platform
if platform.platform().startswith('Win'):
    import pygetwindow as gw
import numpy as np
from PIL import Image, ImageGrab
from typing import Tuple
from src.read.read_user_config import file_path


class Screen_Getter:
    @staticmethod
    def get_window_with_title(start_title: str):
        """
        This function will look for a window starts with a specific title
        :param start_title: The starting title of window
        :return: The first window or None if no matching window found
        """
        def get_window_list_win():
            return gw.getAllWindows()

        def get_win_window():
            for window in get_window_list_win():
                if window.title.startswith(start_title):
                    return window
            return None

        return get_win_window()

    @staticmethod
    def get_cropped_window_region(window) -> Tuple[int, int, int, int]:
        """
        Loads user config and return the region with cropping.
        Left(0), Top(1), Height(2), Width(3)
        :param window:
        :return: The cropped region
        """
        with open(file_path, 'rb') as file:
            config = tomllib.load(file)
            config_window = config["window"]

        left = int(window.left + config_window["crop_left"])
        top = int(window.top + config_window["crop_top"])
        height = int(window.height - config_window["crop_bottom"] - config_window["crop_top"])
        width = int(window.width - config_window["crop_right"] - config_window["crop_left"])

        return left, top, height, width

    @staticmethod
    def get_screenshot_of_chosen_window(window) -> Image.Image:
        x = window.left
        y = window.top
        h = window.height
        w = window.width
        return ImageGrab.grab(bbox=(x, y, w+x, h+y))

    @staticmethod
    def get_screenshot_of_chosen_region(region) -> Image.Image:
        x = region[0]
        y = region[1]
        h = region[2]
        w = region[3]
        return ImageGrab.grab(bbox=(x, y, w+x, h+y))

    def get_screenshot_of_chosen_region_cv2(self, region) -> np.ndarray:
        pil_screenshot = self.get_screenshot_of_chosen_region(region)
        cv_screenshot = np.array(pil_screenshot)
        return cv2.cvtColor(cv_screenshot, cv2.COLOR_RGB2BGR)

"""
if __name__ == '__main__':
    with open(file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])
    curr_region = (chosen_window.left, chosen_window.top, chosen_window.height, chosen_window.width)
    chosen_region = screen_getter.get_cropped_window_region(chosen_window)
    screenshot = screen_getter.get_screenshot_of_chosen_region(chosen_region)
"""
