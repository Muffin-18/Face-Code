# typing_speed_tracker.py

import time


class TypingSpeedTracker:

    def __init__(self, text_widget):
        self.text_widget = text_widget

        self.key_times = []
        self.total_keys = 0
        self.backspaces = 0
        self.last_key_time = time.time()

        self.window = 20
        self.text_widget.bind("<Key>", self._on_key)

    def _on_key(self, event):

        now = time.time()
        ignored = {
            "Shift_L", "Shift_R",
            "Control_L", "Control_R",
            "Alt_L", "Alt_R",
            "Caps_Lock"
        }

        if event.keysym not in ignored:
            self.key_times.append(now)
            self.total_keys += 1

        if event.keysym == "BackSpace":
            self.backspaces += 1

        self.last_key_time = now

    def _cpm(self):
        now = time.time()
        self.key_times = [t for t in self.key_times if now - t <= self.window]
        return len(self.key_times) * (60 / self.window)

    def _accuracy(self):
        if self.total_keys == 0:
            return 100
        return ((self.total_keys - self.backspaces) / self.total_keys) * 100

    def _idle(self):
        return time.time() - self.last_key_time

    def _confidence(self, cpm, accuracy, idle):

        speed_score = min((cpm / 250) * 100, 100)
        idle_penalty = min(idle * 1.5, 100)

        return max(0, min(
            0.4 * speed_score +
            0.5 * accuracy -
            0.3 * idle_penalty,
            100
        ))

    def get_typing_metrics(self):
        cpm = self._cpm()
        acc = self._accuracy()
        idle = self._idle()
        conf = self._confidence(cpm, acc, idle)
        return conf, idle, acc