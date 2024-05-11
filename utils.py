import requests
import time
import database as db
import genai

def generateId(source, destination):
    return f"{str(round(time.time()*1000))}{source[:2]}{destination[:2]}"

def currencyRate(currency):
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}").json()
    return response

def contentGen(city, forceGen=False):
    contentDb = db.getContentData(city)
    if not forceGen and contentDb != None:
        return
    data = genai.contentCreator(city)
    db.postContentData(city, data)
    print("Content Generated!")