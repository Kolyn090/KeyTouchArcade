import json
import time
import tomllib
import atexit
from src.read import read_user_config, read_system_config
from src.util.screen_getter import Screen_Getter
from src.control.gamepad import Gamepad
from src.control.joystick import Joystick
from src.util.prop2pos import prop2pos


if __name__ == '__main__':
    with open(read_user_config.file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])

    with open(read_system_config.file_path, 'r') as file:
        data = json.load(file)
        key_properties = data["system"]["key-proportions"]

    joystick_pos = prop2pos(chosen_window, key_properties["joy-stick"])
    joystick = Joystick(joystick_pos, y_factor=1.0)
    gamepad = Gamepad(chosen_window)

    atexit.register(joystick.cleanup)
    atexit.register(gamepad.cleanup)

    joystick.process.start()
    gamepad.process.start()
