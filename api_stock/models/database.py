from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.depositos_collection = None
        self.movimientos_collection = None

    def connect(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"), maxPoolSize=50, minPoolSize=5)
        self.db = self.client["dietetica"]
        self.depositos_collection = self.db["depositos"]
        self.movimientos_collection = self.db["movimientos"]


    def disconnect(self):
        if self.client:
            self.client.close()

db = Database()
