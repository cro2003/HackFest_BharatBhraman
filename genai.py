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

#print(contentCreator("Mumbai"))