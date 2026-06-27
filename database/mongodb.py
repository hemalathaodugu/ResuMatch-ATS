from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

uri = "mongodb+srv://hemalatha:hemalatha@cluster0.ayavnqi.mongodb.net/?appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client["ResuMatch"]

candidates = db["Candidates"]

print("MongoDB Connected Successfully!")


def save_candidate(data):

    result = candidates.insert_one(data)

    print("Saved ID:", result.inserted_id)


def delete_candidate(id):

    candidates.delete_one(
        {
            "_id": ObjectId(id)
        }
    )


def get_candidate(id):

    return candidates.find_one(
        {
            "_id": ObjectId(id)
        }
    )