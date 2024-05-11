import requests
import time

def generateId(source, destination):
    return f"{str(round(time.time()*1000))}{source[:2]}{destination[:2]}"

def currencyRate(currency):
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}").json()
    return response