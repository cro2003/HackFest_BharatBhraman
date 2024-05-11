from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
LANGUAGE_DATA_OBJ_ID = os.environ.get('LANGUAGE_DATA_OBJ_ID')
CONTENT_OBJ_ID = os.environ.get('CONTENT_OBJ_ID')
GUIDE_OBJ_ID = os.environ.get('GUIDE_OBJ_ID')
USER_OBJ_ID = os.environ.get('USER_OBJ_ID')
cluster = MongoClient(f"mongodb+srv://{username}:{password}@cluster0-pqz66.mongodb.net/?authSource=admin")
db = cluster['BharatBhraman']
collections_manager = db['BharatBhraman']

def getAllData(objId):
    return collections_manager.find_one({"_id": ObjectId(objId)})

def getContentData(city):
    return getAllData(CONTENT_OBJ_ID).get('content').get(city)

def postContentData(city, data):
    collections_manager.update_one({"_id": ObjectId(CONTENT_OBJ_ID)}, {"$set": {f"content.{city}": data}})
    for place in data:
        collections_manager.update_one({"_id": ObjectId(GUIDE_OBJ_ID)}, {"$set": {place['placeName']: []}})
def getGuidePlace():
    allData = getAllData(GUIDE_OBJ_ID)
    placeList = [placeName for placeName in allData.keys()]
    return placeList

def postGuideData(placeName, data):
    collections_manager.update_one({"_id": ObjectId(GUIDE_OBJ_ID)}, {"$push": {placeName: data}})
    contentData = getContentData(data['city'])
    for idx in range(len(contentData)):
        if contentData[idx]['placeName'] == placeName:
            contentData[idx]['guide'] = [] #TEMP
            contentData[idx]['guide'].append(data)
            collections_manager.update_one({"_id": ObjectId(CONTENT_OBJ_ID), f"content.{data['city']}.placeName": placeName}, {'$set': {f"content.{data['city']}.$": contentData[idx]}})
            return

def showGuide(placeName):
    allData = getAllData(GUIDE_OBJ_ID)
    return allData.get(placeName)

def registerUser(username, password):
    collections_manager.update_one({"_id": ObjectId(USER_OBJ_ID)}, {"$set": {username: password, "orders": []}})

def checkUser(username, password):
    allData = getAllData(USER_OBJ_ID)
    if allData.get(username) == password:
        return True
    return False

def registerGuide(username, password):
    collections_manager.update_one({"_id": ObjectId(GUIDE_OBJ_ID)}, {"$set": {username: password, "orders": []}})


languageData = getAllData(LANGUAGE_DATA_OBJ_ID).get('languageData')
currency = getAllData(LANGUAGE_DATA_OBJ_ID).get('currency')
guideDetails = getAllData(LANGUAGE_DATA_OBJ_ID).get('guideDetails')
flightCodes = getAllData(LANGUAGE_DATA_OBJ_ID).get('flightCodes')