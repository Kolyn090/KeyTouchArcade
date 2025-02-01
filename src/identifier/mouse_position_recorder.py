import math
import tomllib
import threading
from enum import Enum
from typing import Tuple
from pynput import keyboard
from pynput.mouse import Controller
from src.identifier.key_proportions_manager import Key_Proportions_Manager
from src.util.prop2pos import prop2pos
from src.util.pos2prop import pos2prop
from src.util.screen_getter import Screen_Getter
from src.read.read_user_config import file_path


class Key_Status(Enum):
    UNCHANGED=1
    CHANGED=2
    NEW=3


class Mouse_Position_Recorder:
    def __init__(self):
        self.choosing_key = ""
        self.mouse = Controller()
        self.pressing = set()
        self.running = True
        self.recorded = {}
        self.kpm = Key_Proportions_Manager()

        with open(file_path, 'rb') as file:
            config = tomllib.load(file)
            config_window = config["window"]
        screen_getter = Screen_Getter()
        self.chosen_window = screen_getter.get_window_with_title(config_window["name"])

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        self.stop_keys = {keyboard.Key.esc}
        self.stop_event = threading.Event()

    def on_press(self, key):
        if not self.running:
            return

        key_char = self.get_char(key)
        self.pressing.add(key_char)

        if key in self.stop_keys:
            print(f"\n⚠️ Stopping key '{key_char}' pressed. ⚠️\n")
            self.running = False
            self.pressing.clear()
            self.stop_event.set()

    def on_release(self, key):
        if not self.running:
            return

        key_char = self.get_char(key)
        if key_char in self.pressing:
            self.pressing.remove(key_char)

        mouse_position = list(self.mouse.position)
        self.record(key_char, mouse_position)

    @staticmethod
    def get_char(key):
        if hasattr(key, 'char'):
            return key.char
        return str(key)

    def record(self, key, position):
        print(f"\nRecording {{{key}}}: {position}")
        self.recorded[key] = position

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        def get_ask_message():
            BOLD = "\033[1m"
            UNDERLINE = "\033[4m"
            GREEN = "\033[92m"
            RESET = "\033[0m"
            RED = "\033[91m"
            return (
                f"{BOLD}{UNDERLINE}{GREEN}"
                f"\nDo you want to save?[Y/{RED}N{GREEN}]\n\n"
                f"{RESET}"
            )

        def get_save_message():
            BOLD = "\033[1m"
            UNDERLINE = "\033[4m"
            GREEN = "\033[92m"
            RESET = "\033[0m"
            YELLOW = "\033[93m"
            return (
                f"{BOLD}{UNDERLINE}{GREEN}✔️ Your changes have been "
                f"{YELLOW}SAVED{RESET}{BOLD}{UNDERLINE}{GREEN}! {RESET}\n"
            )

        def get_discard_message():
            BOLD = "\033[1m"
            UNDERLINE = "\033[4m"
            GREEN = "\033[92m"
            RESET = "\033[0m"
            RED = "\033[91m"
            return (
                f"{BOLD}{UNDERLINE}{GREEN}❌ Your changes have been "
                f"{RED}DISCARDED{RESET}{BOLD}{UNDERLINE}{GREEN}! {RESET}\n"
            )

        def get_continue_message():
            BOLD = "\033[1m"
            UNDERLINE = "\033[4m"
            GREEN = "\033[92m"
            RESET = "\033[0m"
            YELLOW = "\033[93m"
            return (
                f"{BOLD}{UNDERLINE}{GREEN} Press {YELLOW}'Return'{GREEN} to continue. {RESET}\n"
            )

        def clear_input_area():
            input(get_continue_message())

        def save(_key_proportions):
            self.kpm.save_key_proportions(_key_proportions)

        keys_status_and_key_proportions = self.get_keys_status_and_new_key_proportions()
        keys_status = keys_status_and_key_proportions[0]
        key_proportions = keys_status_and_key_proportions[1]

        self.print_recorded_table(keys_status, key_proportions)
        clear_input_area()

        ask = input(get_ask_message())
        ask = ask.strip()
        if ask == 'n' or ask == 'N':
            print(get_discard_message())
        else:
            save(key_proportions)
            print(get_save_message())
        return False

    def print_recorded_table(self, keys_status, key_proportions):
        def pad_with(text, total_length, fill=' '):
            if len(text) >= total_length:
                return text
            padding_needed = total_length - len(text)
            return text + fill * padding_needed

        def get_len_longest_key_among(ds: list[dict]):
            def get_len_longest_key(_d: dict):
                if not _d:
                    return 0
                return max(len(str(_key)) for _key in _d.keys())

            result = 0
            for d in ds:
                curr = get_len_longest_key(d)
                result = max(result, curr)

            return result

        len_longest_key = get_len_longest_key_among([self.recorded, key_proportions])
        if len_longest_key < len('Key'):
            len_longest_key = len('Key')

        # region PrintTable
        BOLD = "\033[1m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        RESET = "\033[0m"

        message = (f"{BOLD}{GREEN}\n{pad_with('Key', len_longest_key)} {RESET}"
                   f"{BOLD}{GREEN}| Value\n{pad_with('', len_longest_key+1, '-')}{RESET}"
                   f"{BOLD}{GREEN}|-------------------{RESET}\n")
        curr_key_proportions = self.kpm.get_key_proportions()

        for key, key_status in keys_status.items():
            value = key_proportions[key]
            if key_status == Key_Status.NEW:
                message += (f"{BOLD}{YELLOW}{pad_with(key, len_longest_key)} {GREEN}| "
                            f"{YELLOW}NEW: {value}{RESET}\n")
            elif key_status == Key_Status.UNCHANGED:
                message += (f"{BOLD}{GREEN}{pad_with(key, len_longest_key)} | "
                            f"UCD: {value}{RESET}\n")
            else: # Key_Status.CHANGED
                message += (f"{BOLD}{RED}{pad_with(key, len_longest_key)} {GREEN}| "
                            f"{RED}CHG: {curr_key_proportions[key]} -> {value}{RESET}\n")
        print(message)
        # endregion

    def get_keys_status_and_new_key_proportions(self) -> (dict[str, Key_Status], dict[str, list]):
        def are_lists_equal(list1, list2, rel_tol=1e-9, abs_tol=0.0):
            if len(list1) != len(list2):
                return False
            return all(math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in zip(list1, list2))

        result = {}
        curr_key_proportions = self.kpm.get_key_proportions()
        new_key_proportions = curr_key_proportions.copy()

        # Compare keys in system config with user mentioned keys
        for key, value in self.recorded.items():
            if key in curr_key_proportions:
                new_prop = self.get_proportion_on_window_by_position(value)
                if are_lists_equal(new_prop, curr_key_proportions[key]):
                    result[key] = Key_Status.UNCHANGED
                else: # CHANGED
                    result[key] = Key_Status.CHANGED
                    new_prop = self.get_proportion_on_window_by_position(value)
                    new_key_proportions[key] = [new_prop[0], new_prop[1]]
            else:
                result[key] = Key_Status.NEW
                new_prop = self.get_proportion_on_window_by_position(value)
                new_key_proportions[key] = [new_prop[0], new_prop[1]]

        # Keys in system config but did not mention by user this time
        for key in curr_key_proportions.keys():
            if key not in self.recorded:
                result[key] = Key_Status.UNCHANGED

        return result, new_key_proportions

    def get_position_on_window_by_proportion(self, prop) -> Tuple[int, int]:
        result = prop2pos(self.chosen_window, prop)
        return round(result[0], 2), round(result[1], 2)

    def get_proportion_on_window_by_position(self, pos) -> Tuple[float, float]:
        result = pos2prop(self.chosen_window, pos)
        return round(result[0], 2), round(result[1], 2)

    @staticmethod
    def get_welcome_message():
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        CYAN = "\033[96m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        return (
            f"{BOLD}{UNDERLINE}{CYAN}🖱️  Mouse Position Recorder 🖱️{RESET}\n\n"
            f"{BOLD}➡️  Hover your mouse over the desired position on the window.{RESET}\n"
            f"{BOLD}⌨️  Press {YELLOW}ANY KEY{RESET}{BOLD} to record the position.{RESET}\n"
            f"{BOLD}❌  Press the {YELLOW}'Esc'{RESET}{BOLD} key to stop recording.{RESET}\n"
        )


if __name__ == '__main__':
    with Mouse_Position_Recorder() as mpr:
        print(mpr.get_welcome_message())
        while mpr.running:
            mpr.stop_event.wait()

