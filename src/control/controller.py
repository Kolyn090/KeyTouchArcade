import tomllib
import atexit
from src.read import read_user_config
from src.util.screen_getter import Screen_Getter
from src.control.gamepad import Gamepad
from src.control.joystick import Joystick
from src.util.prop2pos import prop2pos


if __name__ == '__main__':
    with open(read_user_config.file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]
        config_joystick = config["joystick"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])

    joystick_x_factor = config_joystick["x_factor"]
    joystick_y_factor = config_joystick["y_factor"]
    joystick_pos = prop2pos(chosen_window, (
        config_joystick["x_proportion"],
        config_joystick['y_proportion']
    ))
    joystick = Joystick(joystick_pos, x_factor=joystick_x_factor, y_factor=joystick_y_factor)
    gamepad = Gamepad(chosen_window)

    atexit.register(joystick.cleanup)
    atexit.register(gamepad.cleanup)

    joystick.process.start()
    gamepad.process.start()
