from datetime import datetime

class Session:
    def __init__(self, start_time, end_time=None, duration=0):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration

    def to_dict(self):
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }
