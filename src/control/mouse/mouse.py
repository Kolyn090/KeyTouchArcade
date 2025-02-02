import os
from src.control.mouse.mouse_c import Mouse_C


class Mouse:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(script_dir, 'mice.dll')
        self._mouse_c = Mouse_C(dll_path)
        self._client = self._mouse_c.vmulti_alloc()

    def click(self, x, y, touch_width=10, touch_height=10, press_duration=0.5):
        if self._mouse_c.vmulti_connect(self._client):
            self._mouse_c.click(self._client, x, y, touch_width, touch_height, press_duration)

    def free(self):
        """
        Disconnect and free the vmulti client if it exists.
        :return:
        """
        if self._client:
            self._mouse_c.vmulti_disconnect(self._client)
            self._mouse_c.vmulti_free(self._client)  # Free the client
            self._client = None  # Avoid double freeing

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.free()


if __name__ == '__main__':
    mouse = Mouse()
    with mouse:
        mouse.click(300, 300)
        mouse.click(300, 300)
        mouse.click(300, 300)
