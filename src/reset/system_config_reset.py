import json
from src.read.read_system_config import file_path


def reset_system_config():
    new_system_config = """
    {
      "system": {
        "key-proportions": {
          "joy-stick": [0.5, 0.5]
        }
      }
    }
    """
    data = json.loads(new_system_config)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
