import requests

def getStation(query):
    response = requests.get('https://api.railyatri.in//api/common_city_station_search.json', params={'q': query}).json()
    if response['items'] == []:
        return []
    return response['items'][0]

def getTrainDetails(source, destination, date):
    srcStnInfo = getStation(source)
    destStnInfo = getStation(destination)
    if srcStnInfo == [] or destStnInfo == []:
        return {"error": "station not found"}
    params = {
        'from': srcStnInfo['station_code'],
        'to': destStnInfo['station_code'],
        'dateOfJourney': date,
        'action': 'train_between_station',
        'controller': 'train_ticket_tbs',
        'device_type_id': '2',
        'from_code': srcStnInfo['station_code'],
        'from_name': srcStnInfo['station_name'],
        'journey_date': date,
        'journey_quota': 'GN',
        'to_code': destStnInfo['station_code'],
        'to_name': destStnInfo['station_name'],
        'v_code': '167',
    }
    data = []
    fareFetchList = []
    response = requests.get('https://api.railyatri.in/api/trains-between-station-from-wrapper.json',
                            params=params).json()
    if response.get('error')!=None or response["train_between_stations"]==[]:
        return []
    for index, trainInfo in enumerate(response["train_between_stations"]):
        postData = {
            'train_number': trainInfo['train_number'],
            'journey_date': f'{date} ',
            'boarding_from': trainInfo['from'],
            'boarding_to': trainInfo['to'],
            'journey_class': [
                '3A',
                'CC',
                '3E',
                'SL',
                '2A'
            ],
            'quota': 'GN',
            'urgency': False,
            'd_day': 0,
        }
        fareFetchList.append(postData)
        main = {
            "trainNo": trainInfo['train_number'],
            "trainName": trainInfo['train_name'],
            "source": trainInfo['from_station_name'],
            "departure": trainInfo['from_std'],
            "destination": trainInfo['to_station_name'],
            "arrival": trainInfo['to_sta'],
            #"fare": f'{price:,}',
            "duration": trainInfo['duration']
        }
        data.append(main)
    fareData = fareCheckerTrain(fareFetchList)
    for index, fare in enumerate(fareData):
        data[index]["fare"] = fare
    return data

def fareCheckerTrain(data):
    fare = requests.post('https://trainticketapi.railyatri.in/api/seat-availability-from-db',
                         json={'device_type_id': '2', 'train_details': data,
                             'quota': 'GN',
                             'urgency': False,
                             'd_day': 0,
                         }).json()
    fareData = []
    prevPrice = 1911
    for trains in fare['train_data']:
        if trains["class_data"][0]["success"] == True:
            price = trains["class_data"][0]["seat_availibility"][0]["total_fare"]
        elif trains["class_data"][1]["success"] == True:
            price = trains["class_data"][1]["seat_availibility"][0]["total_fare"]
        elif trains["class_data"][2]["success"] == True:
            price = trains["class_data"][2]["seat_availibility"][0]["total_fare"]
        elif trains["class_data"][3]["success"] == True:
            price = trains["class_data"][3]["seat_availibility"][0]["total_fare"]
        else:
            price = prevPrice
            print(trains)
        prevPrice = price
        fareData.append(price)
    return fareData