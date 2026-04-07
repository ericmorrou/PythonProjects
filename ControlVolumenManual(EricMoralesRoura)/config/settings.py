import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
    config = {
        "MONGODB_URI": os.getenv("MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "hand_tracking_db")
    }
    return config
