import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from datetime import timezone
import database as db

load_dotenv()
header = {
    'apikey': os.environ.get('FLIGHT'),
}
def getAirport(query, dest=False):
    params = {
        'term': query,
        'locale': 'en-US',
        'location_types': 'airport',
        'limit': '10',
        'active_only': 'true',
    }
    response = requests.get('https://api.tequila.kiwi.com/locations/query', params=params, headers=header).json()
    if response['locations'] == [] or (response['locations'][0]['city']['country']['id'] != 'IN' and dest):
        return []
    return response['locations'][0]['code']

def getFlightDetails(source, destination, date):
    srcCode = getAirport(source)
    destCode = getAirport(destination, dest=True)
    if srcCode == [] or destCode == []:
        return []
    params = {
        'fly_from': getAirport(source),
        'fly_to': getAirport(destination),
        'date_from': date,
        'date_to': date,
        'partner_market': 'in',
        'curr': 'INR',
        'locale': 'en',
    }
    response = requests.get('https://api.tequila.kiwi.com/v2/search', params=params, headers=header).json()
    if response['data'] == []:
        return []
    data = []
    for routes in response['data']:
        flightId = ""
        departureDate = datetime.fromisoformat(routes['local_departure'][:-1]).astimezone(timezone.utc)
        arrivalDate = datetime.fromisoformat(routes['local_arrival'][:-1]).astimezone(timezone.utc)
        for flights in routes["route"]:
            flightId += flights['airline'] + "-" + str(flights['flight_no']) + ", "
        compiledData = {
            "flightName": db.flightCodes[routes['airlines'][0]],
            "flightId": flightId[:-2],
            "departure": departureDate.strftime('%H:%M'),
            "arrival": arrivalDate.strftime('%H:%M'),
            "arrivalDate": arrivalDate.strftime('%d-%m-%Y'),
            "src": routes['cityFrom'],
            "destination": routes['cityTo'],
            "duration": f"{str(routes['duration']['departure'] // 3600).zfill(2)}:{str((routes['duration']['departure'] % 3600) // 60).zfill(2)}",
            "fare": f"{round(routes['price']):,} {response['currency']}",
            "currency": response['currency'],
            "destinationCity-en": routes['cityTo']
        }
        data.append(compiledData)
    return data