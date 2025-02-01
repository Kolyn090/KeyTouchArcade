import tomllib
from src.read.read_user_config import file_path
from src.util.screen_getter import Screen_Getter

if __name__ == '__main__':
    with open(file_path, 'rb') as file:
        config = tomllib.load(file)
        config_window = config["window"]

    screen_getter = Screen_Getter()
    chosen_window = screen_getter.get_window_with_title(config_window["name"])
    top = int(config_window["default_top"])
    left = int(config_window["default_left"])
    width = int(config_window["default_width"])
    height = int(config_window["default_height"])

    if chosen_window:
        chosen_window.activate()
        chosen_window.moveTo(left, top)
        chosen_window.resizeTo(width, height)
        print(f"Window resized to top-left ({left}, {top}) with width {width} and height {height}.")
    else:
        print('Window not found, cannot rescale')
