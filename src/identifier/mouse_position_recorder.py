import threading
from enum import Enum
from pynput import keyboard
from pynput.mouse import Controller
from src.identifier.key_proportions_manager import Key_Proportions_Manager


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

        self.print_recorded_table()
        clear_input_area()

        ask = input(get_ask_message())
        ask = ask.strip()
        if ask == 'n' or ask == 'N':
            print(get_discard_message())
        else:
            print(get_save_message())
        return False

    def print_recorded_table(self):
        def pad_with(text, total_length, fill=' '):
            if len(text) >= total_length:
                return text
            padding_needed = total_length - len(text)
            return text + fill * padding_needed

        def get_len_longest_key_among(ds):
            def get_len_longest_key(_d):
                if not _d:
                    return 0
                return max(len(str(_key)) for _key in _d.keys())

            result = 0
            for d in ds:
                curr = get_len_longest_key(d)
                result = max(result, curr)

            return result

        keys_status_and_key_proportions = self.get_keys_status_and_key_proportions()
        keys_status = keys_status_and_key_proportions[0]
        key_proportions = keys_status_and_key_proportions[1]

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

        for key, key_status in keys_status.items():
            if key in self.recorded:
                value = self.recorded[key]
            else:
                value = key_proportions[key]
            if key_status == Key_Status.NEW:
                message += (f"{BOLD}{YELLOW}{pad_with(key, len_longest_key)} {GREEN}| "
                            f"{YELLOW}NEW: {value}{RESET}\n")
            elif key_status == Key_Status.UNCHANGED:
                message += (f"{BOLD}{GREEN}{pad_with(key, len_longest_key)} | "
                            f"UCD: {value}{RESET}\n")
            else: # Key_Status.CHANGED
                message += (f"{BOLD}{RED}{pad_with(key, len_longest_key)} {GREEN}| "
                            f"{value} -> {RED}CHG: {value}{RESET}\n")
        print(message)
        # endregion

    def get_keys_status_and_key_proportions(self) -> (dict[str, Key_Status], dict[str, list]):
        result = {}
        curr_key_proportions = self.kpm.get_key_proportions()
        for key, value in self.recorded.items():
            if key in curr_key_proportions:
                result[key] = Key_Status.UNCHANGED
                # CHANGED
                # TODO: Need to calculate key proportions
            else:
                result[key] = Key_Status.NEW

        for key in curr_key_proportions.keys():
            if key not in self.recorded:
                result[key] = Key_Status.UNCHANGED

        return result, curr_key_proportions

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
