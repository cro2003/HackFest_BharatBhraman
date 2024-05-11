import requests
import os
import utils
from dotenv import load_dotenv

load_dotenv()
HOTEL_API_KEY = os.environ.get('HOTEL')

def getHotelDetails(location, checkinDate, checkoutDate, currency, type=None): #IN YYYY-MM-DD Form
    hotelData = []
    headers = {
        "X-RapidAPI-Key": HOTEL_API_KEY,
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }
    locationId = requests.get("https://priceline-com-provider.p.rapidapi.com/v1/hotels/locations", headers=headers, params={"name": location, "search_type": "ALL"}).json()[0]["id"]
    exchngRates = utils.currencyRate(currency)
    querystring = {"date_checkout":checkoutDate,"sort_order":"PRICE","location_id":locationId,"date_checkin":checkinDate, "star_rating_ids":"3.0,3.5,4.0,4.5,5.0"}
    if type=="comfort":
        querystring["star_rating_ids"] = "4.0,4.5,5.0"
        querystring["sort_order"] = "HDR"
    hotelInformation = requests.get("https://priceline-com-provider.p.rapidapi.com/v1/hotels/search", headers=headers, params=querystring).json()
    for hotel in hotelInformation["hotels"]:
        """try:
            image = hotel["media"]["url"]
            imageResponse = requests.get(image)
            if not imageResponse.ok: raise TypeError
        except:
            image = 'https://static.vecteezy.com/system/resources/previews/015/694/767/original/skyscraper-hotel-building-flat-cartoon-hand-drawn-illustration-template-with-view-on-city-space-of-street-panorama-design-vector.jpg'"""
        price = round(float(hotel["ratesSummary"]["minPrice"])/ exchngRates["rates"]["USD"])
        try:
            data = {
                "name": hotel["name"],
                "rating": hotel["overallGuestRating"],
                "location": hotel["location"]["address"]["addressLine1"],
                "price": f'{price:,}',
                "image": hotel["media"]["url"],
                "star": hotel["starRating"]
            }
        except:
            continue
        hotelData.append(data)
    return hotelData

