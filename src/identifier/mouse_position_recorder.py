import threading
from pynput import keyboard
from pynput.mouse import Controller


class Mouse_Position_Recorder:
    def __init__(self):
        self.choosing_key = ""
        self.mouse = Controller()
        self.pressing = set()
        self.running = True

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
            print(f"⚠️ Stopping key '{key_char}' pressed. ⚠️")
            self.running = False
            self.pressing.clear()
            self.stop_event.set()  # Trigger the event to stop immediately

    def on_release(self, key):
        if not self.running:
            return

        key_char = self.get_char(key)
        if key_char in self.pressing:
            self.pressing.remove(key_char)
        print(f"\nRecording {{{key_char}}}: {self.mouse.position}")

    @staticmethod
    def get_char(key):
        if hasattr(key, 'char'):
            return key.char
        return str(key)

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
                f"\n\nDo you want to save?[Y/{RED}N{GREEN}]\n\n"
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

        ask = input(get_ask_message())
        ask = ask.strip()
        if ask == '' or ask == 'y' or ask == 'Y':
            print(get_save_message())
        else:
            print(get_discard_message())
        return False

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
