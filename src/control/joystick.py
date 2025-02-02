import json
import tomllib
import multiprocessing
from pynput import keyboard
from pynput.mouse import Button, Controller
from src.util.screen_getter import Screen_Getter
from src.read import read_user_config, read_system_config
from src.util.prop2pos import prop2pos


class Joystick:
    # x_factor and y_factor could be useful if you are playing a bird-view game.
    def __init__(self, default_pos, x_factor=1.0, y_factor=1.0, constraint_range=10.0):
        self.default_pos = default_pos
        self.key_mapping = {
            "w": (0, -constraint_range*y_factor),
            "a": (-constraint_range*x_factor, 0),
            "s": (0, constraint_range*y_factor),
            "d": (constraint_range*x_factor, 0)
        }
        self.cannot_coexist = {
            "w": ["s"],
            "a": ["d"],
            "s": ["w"],
            "d": ["a"]
        }
        self.constraint_range = constraint_range
        self.mouse = Controller()
        self.mouse.position = (int(self.default_pos[0]), int(self.default_pos[1]))

        self.is_pressing = {}
        for key in self.key_mapping.keys():
            self.is_pressing[key] = False

        self.process = multiprocessing.Process(target=self.work)

    def work(self):
        """Starts the keyboard listener."""
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        """Handles key press events for movement."""
        try:
            key_char = self.get_char(key)
            if key_char in self.key_mapping:
                if not self.is_pressing[key_char]:
                    # print("Mouse down.")
                    x, y = self.mouse.position
                    self.mouse.position = (x, y)
                    self.mouse.press(Button.left)
                    self.is_pressing[key_char] = True
                    self.move_mouse(self.cannot_coexist[key_char])
        except AttributeError:
            pass  # Ignore non-character keys

    def on_release(self, key):
        key_char = self.get_char(key)
        if key_char in self.is_pressing:
            self.is_pressing[key_char] = False
            self.move_mouse()
        if all(not value for value in self.is_pressing.values()):
            # print("Mouse up.")
            x, y = self.mouse.position
            self.mouse.position = (x, y)
            self.mouse.release(Button.left)
            self.mouse.position = (int(self.default_pos[0]), int(self.default_pos[1]))

    @staticmethod
    def get_char(key):
        if hasattr(key, 'char'):
            return key.char

    def move_mouse(self, ignore_keys=None):
        new_pos_x = self.default_pos[0]
        new_pos_y = self.default_pos[1]
        for key in self.key_mapping:
            if not ignore_keys or key not in ignore_keys:
                if self.is_pressing[key]:
                    result_x = new_pos_x + self.key_mapping[key][0]
                    result_y = new_pos_y + self.key_mapping[key][1]

                    if result_x != self.default_pos[0]:
                        new_pos_x = result_x
                    if result_y != self.default_pos[1]:
                        new_pos_y = result_y
        self.mouse.position = (int(new_pos_x), int(new_pos_y))


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
    joystick.process.start()
