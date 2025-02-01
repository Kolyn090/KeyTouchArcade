import json
import tomllib
import cv2
from src.read import read_system_config, read_user_config
from src.util.screen_getter import Screen_Getter
from src.util.prop2pos import prop2pos


if __name__ == '__main__':
    with open(read_user_config.file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])

    # screen_getter.get_screenshot_of_chosen_window(chosen_window).save('test.png')
    # cropped = screen_getter.get_cropped_window_region(chosen_window)
    # s = screen_getter.get_screenshot_of_chosen_region(cropped)
    # s.save('cropped.png')

    chosen_region = screen_getter.get_cropped_window_region(chosen_window)
    curr_region = (chosen_window.left, chosen_window.top, chosen_window.height, chosen_window.width)
    # print(chosen_region, curr_region)

    screenshot = screen_getter.get_screenshot_of_chosen_region_cv2(chosen_region)

    with open(read_system_config.file_path, 'r') as file:
        data = json.load(file)
        key_proportions = data["system"]["key-proportions"]

    for key, prop in key_proportions.items():
        pos = prop2pos(chosen_window, prop)
        pos = [pos[0] - chosen_region[0], pos[1] - chosen_region[1]]
        cv2.circle(screenshot, pos, radius=2, color=(0, 0, 255), thickness=-1)
        cv2.imwrite('dotted.png', screenshot)
