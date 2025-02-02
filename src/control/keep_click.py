import time

class Keep_Click:
    def __init__(self, key_char, rest_interval=0.5):
        self.curr_time = time.time()
        self.key_char = key_char
        self.rest_interval = rest_interval

    def can_click(self):
        curr_time = time.time()
        if curr_time - self.curr_time >= self.rest_interval:
            self.curr_time = curr_time
        else:
            return False
        return True
