import os
import tomllib
from src.read import read_user_config

with open(read_user_config.file_path, 'rb') as file:
    config = tomllib.load(file)
    system_config_path = config["system-config"]["path"]

_current_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_current_dir, '..', '..'))
file_path = os.path.join(_project_root, system_config_path)
