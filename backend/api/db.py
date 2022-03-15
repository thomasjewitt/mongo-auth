from pymongo import MongoClient
from typing import Dict


class DBManager():

    def __init__(self):
        self.client = MongoClient("mongodb://db:27017/")
        self.db = self.client["db"]
        self.users = self.db["users"]
        self.users.create_index('email', unique=True)  # Ensure that the email field for users is unique.
    
    def add_user_to_db(self, user: Dict):
        id = self.users.insert_one(user).inserted_id
        result = self.users.find_one({"_id": id})
        return result

    def retrieve_user_by_email(self, email: str):
        return self.users.find_one({"email": email})