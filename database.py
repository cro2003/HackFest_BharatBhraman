from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
LANGUAGE_DATA_OBJ_ID = os.environ.get('LANGUAGE_DATA_OBJ_ID')
CONTENT_OBJ_ID = os.environ.get('CONTENT_OBJ_ID')
cluster = MongoClient(f"mongodb+srv://{username}:{password}@cluster0-pqz66.mongodb.net/?authSource=admin")
db = cluster['BharatBhraman']
collections_manager = db['BharatBhraman']

def getAllData(objId):
    return collections_manager.find_one({"_id": ObjectId(objId)})

def getContentData(city):
    return getAllData(CONTENT_OBJ_ID).get('content').get(city)

def postContentData(city, data):
    collections_manager.update_one({"_id": ObjectId(CONTENT_OBJ_ID)}, {"$set": {f"content.{city}": data}})

languageData = getAllData(LANGUAGE_DATA_OBJ_ID).get('languageData')
currency = getAllData(LANGUAGE_DATA_OBJ_ID).get('currency')
guideDetails = getAllData(LANGUAGE_DATA_OBJ_ID).get('guideDetails')
flightCodes = getAllData(LANGUAGE_DATA_OBJ_ID).get('flightCodes')