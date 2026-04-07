import os
from pymongo import MongoClient
from threading import Lock

class MongoDBDAO:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoDBDAO, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("DATABASE_NAME", "hand_tracking_db")
        
        if not self.uri:
            print("Warning: MONGODB_URI not found in environment variables.")
            self.client = None
            self.db = None
        else:
            try:
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
                # Test connection
                self.client.server_info()
                self.db = self.client[self.db_name]
                print(f"Connected to MongoDB Atlas: {self.db_name}")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                self.client = None
                self.db = None
        
        self._initialized = True

    def insert_session(self, session):
        if self.db is not None:
            return self.db.sessions.insert_one(session.to_dict())
        return None

    def insert_volume_event(self, event):
        if self.db is not None:
            return self.db.volume_events.insert_one(event.to_dict())
        return None

    def is_connected(self):
        return self.db is not None
