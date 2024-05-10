import requests
import os
from dotenv import load_dotenv

load_dotenv()
LOCATION_API_KEY = os.environ.get('LOCATION')

def getLocation(query):
    response = requests.get(f"https://api.geoapify.com/v1/geocode/search?text={query}&format=json&apiKey={LOCATION_API_KEY}").json()['results']
    if response == []:
        return []
    return response[0]

def nearestLocation(destInfo):
    data = '{"mode":"drive","sources":[{"location":[72.878176,19.0785451]},{"location":[' + str(
        destInfo['lon']) + ',' + str(destInfo[
                                         'lat']) + ']},{"location":[77.2090057,28.6138954]}],"targets":[{"location":[72.878176,19.0785451]},{"location":[' + str(
        destInfo['lon']) + ',' + str(destInfo['lat']) + ']},{"location":[77.2090057,28.6138954]}]}'

    getDistance = requests.post(f"https://api.geoapify.com/v1/routematrix?apiKey={LOCATION_API_KEY}",
                                headers={"Content-Type": "application/json"}, data=data).json()
    if getDistance['sources_to_targets'][0][1]['distance'] < getDistance['sources_to_targets'][2][1]['distance']:
        return "Mumbai"
    else:
        return "Delhi"