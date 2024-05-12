import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
from imageSearcher import ImageSearcher
import database as db
import threading

load_dotenv()
allContent = {}
genai.configure(api_key=os.getenv('GEMINI_PRO'))
model = genai.GenerativeModel('gemini-pro')

def contentCreator(city):
    print(city)
    threads = []
    content = model.generate_content('Give 6 Places to Visit in ' + city + ' in given json format {places:[{"placeName":  PLACE_NAME, "description":  DETAILED_DESCRIPTION_WITH_AT_LEAST_30_WORDS, "address": FULL_ADDRESS_OF_THE_PLACE}]}',generation_config=genai.types.GenerationConfig(max_output_tokens=2048))
    content.resolve()
    data = content.text[content.text.find('{'):]
    data = data[:data.rfind('}') + 1]
    data = json.loads(data)
    allContent[city] = data['places']
    for index in range(len(allContent[city])):
        thread = threading.Thread(target=searchImage, args=(allContent[city][index]['placeName'] + " " + city, city, index))
        thread.start()
        threads.append(thread)
        searchFormat = (allContent[city][index]['placeName'] + " " + city).replace(' ', '%20')
        allContent[city][index]["mapsDeeplink"] = "https://www.google.com/maps/search/?api=1&query=" + searchFormat
        allContent[city][index]["guide"] = []
        print(allContent[city][index])
    for thread in threads:
        thread.join()
    return allContent[city]

def searchImage(query, city, index):
    image = ImageSearcher(query)
    allContent[city][index]["imageUrl"] = image.run()

def chatbotResponse(userText):
    data = db.getTripData()
    format = f' SYSTEM PROMPT: You are all In one Travel Guru, Here is Trip planned by User is Departing from {data["sourceData"]["city"]} '
    if data.get("flightData") != None:
         format += f', where he will be using Flight From {data["flightData"]["src"]} at {data["flightData"]["departure"]}, the duration of Flight will be {data["flightData"]["duration"]} then it will land at {data["flightData"]["destination"]} on {data["flightData"]["arrival"]} which is priced at {data["flightData"]["fare"]} and the Name of the Flights was {data["flightData"]["flightName"]} and Flight Number were {data["flightData"]["flightId"]} after that User has to pick the Train from {data["trainData"]["source"]} at {data["trainData"]["departure"]} then Reach after {data["trainData"]["duration"]} at {data["trainData"]["destination"]} on {data["trainData"]["arrival"]} priced at {data["trainData"]["fare"]} {data["flightData"]["currency"]} the Train Name was {data["trainData"]["trainName"]} & Train Number {data["trainData"]["trainNo"]} after that Hotel Stay is been Done at {data["hotelData"]["name"]}, Address {data["hotelData"]["location"]} which have User Rating of {data["hotelData"]["rating"]} which is priced at {data["hotelData"]["price"]} {data["flightData"]["currency"]}'
    response = model.generate_content("USER PROMPT: " + userText + format)
    text = response.text.replace("**", "*").replace("*", "\n")
    return text

#print(contentCreator("Mumbai"))