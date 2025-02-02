import os
import time
import tomllib
from multiprocessing import Process
from pynput import keyboard
from src.control.mouse.mouse_c import Mouse_C
from src.util.screen_getter import Screen_Getter
from src.identifier.key_proportions_manager import Key_Proportions_Manager
from src.util.prop2pos import prop2pos
from src.read import read_user_config


class Gamepad:
    def __init__(self, window):
        kpm = Key_Proportions_Manager()
        key_properties = kpm.get_key_proportions()
        self.key_mapping = {}
        for key, key_prop in key_properties.items():
            self.key_mapping[key] = prop2pos(window, (key_prop[0], key_prop[1]))
        self.is_pressing = {}
        for key in self.key_mapping.keys():
            self.is_pressing[key] = False
        self.process = Process(target=self.work)
        self.process.daemon = False

    def work(self):
        """Starts the keyboard listener."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(script_dir, './mouse/mice.dll')
        if not hasattr(self, "mouse_c"):
            self.mouse_c = Mouse_C(dll_path)
            self.vmulti_client = self.mouse_c.create_client()

        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        """Detects key presses and triggers actions."""
        key_char = self.get_char(key)

        def click(target_pos):
            self.mouse_c.click(self.vmulti_client,
                               int(target_pos[0]),
                               int(target_pos[1]),
                               press_duration=0.2)
            self.is_pressing[key_char] = True

        if key_char in self.key_mapping:
            target_pos = self.key_mapping[key_char]
            # print(f"Pressed {key_char}")
            if not self.is_pressing[key_char]:
                click(target_pos)

    def on_release(self, key):
        key_char = self.get_char(key)
        if key_char in self.is_pressing:
            self.is_pressing[key_char] = False

    @staticmethod
    def get_char(key):
        if hasattr(key, 'char'):
            return key.char
        return str(key)

    def cleanup(self):
        if self.mouse_c:
            self.mouse_c.vmulti_disconnect(self.vmulti_client)
            self.mouse_c.vmulti_free(self.vmulti_client)
            print("Disconnected and freed mouse_c.")
        self.process.join()


if __name__ == '__main__':
    with open(read_user_config.file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])
    with Gamepad(chosen_window) as gamepad:
        while True:
            time.sleep(0.2)
