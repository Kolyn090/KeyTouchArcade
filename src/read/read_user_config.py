import os

_current_dir = os.path.dirname(__file__)
_project_root = os.path.abspath(os.path.join(_current_dir, '..', '..'))
file_path = os.path.join(_project_root, 'user-config.toml')
