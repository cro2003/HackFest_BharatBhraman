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
    # format = f' SYSTEM PROMPT: You are all In one Travel Guru, Here is Trip planned by User is Departing from {languageData["plannedTrip"]["sourceData"]["city"]} '
    # if languageData["plannedTrip"]["flightData"] != []:
    #     format += f', where he will be using Flight From {languageData["plannedTrip"]["flightData"]["src"]} at {languageData["plannedTrip"]["flightData"]["departure"]}, the duration of Flight will be {languageData["plannedTrip"]["flightData"]["duration"]} then it will land at {languageData["plannedTrip"]["flightData"]["destination"]} on {languageData["plannedTrip"]["flightData"]["arrival"]} which is priced at {languageData["plannedTrip"]["flightData"]["fare"]} and the Name of the Flights was {languageData["plannedTrip"]["flightData"]["flightName"]} and Flight Number were {languageData["plannedTrip"]["flightData"]["flightId"]} after that User has to pick the Train from {languageData["plannedTrip"]["trainData"]["source"]} at {languageData["plannedTrip"]["trainData"]["departure"]} then Reach after {languageData["plannedTrip"]["trainData"]["duration"]} at {languageData["plannedTrip"]["trainData"]["destination"]} on {languageData["plannedTrip"]["trainData"]["arrival"]} priced at {languageData["plannedTrip"]["trainData"]["fare"]} {languageData["plannedTrip"]["flightData"]["currency"]} the Train Name was {languageData["plannedTrip"]["trainData"]["trainName"]} & Train Number {languageData["plannedTrip"]["trainData"]["trainNo"]} after that Hotel Stay is been Done at {languageData["plannedTrip"]["hotelData"]["name"]}, Address {languageData["plannedTrip"]["hotelData"]["location"]} which have User Rating of {languageData["plannedTrip"]["hotelData"]["rating"]} which is priced at {languageData["plannedTrip"]["hotelData"]["price"]} {languageData["plannedTrip"]["flightData"]["currency"]}'
    # response = model.generate_content("USER PROMPT: " + userText + format)  # for the gemini AI model
    # text = response.text.replace("**", "*").replace("*", "\n")
    # return text
    working = True

#print(contentCreator("Mumbai"))