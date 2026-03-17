from datetime import datetime

class VolumeEvent:
    def __init__(self, prev_volume, new_volume, distance, timestamp=None):
        self.timestamp = timestamp if timestamp else datetime.now()
        self.prev_volume = prev_volume
        self.new_volume = new_volume
        self.distance = distance

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "prev_volume": self.prev_volume,
            "new_volume": self.new_volume,
            "distance": self.distance
        }
