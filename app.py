from flask import Flask, request, render_template, redirect, url_for, flash
import database as db
import os
from dotenv import load_dotenv
from datetime import timedelta
import time
import flight
import location
import train
import hotel
import json

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)
session = {}



@app.route('/', methods=['GET', 'POST'])
def index():
    defaultLang = "en"
    if request.method=='POST':
        defaultLang = request.form['selectedLang']
    return render_template('index.html', supportedLanguage = db.languageData['supportedLanguages'], pageLang = {"language": defaultLang, "codeToLang":  db.languageData["codeToLang"], "translatedData": db.languageData["translatedData"][defaultLang]["index"]})

@app.route('/plan-trip', methods=['POST'])
def planTrip():
    prefferedLang = request.form['selectedLang'].strip()
    source = request.form['from']
    destination = request.form['to']
    date = request.form['date']
    sourceData = location.getLocation(source)
    destData = location.getLocation(destination)
    if sourceData==[] or destData==[] or destData.get('city')==None or sourceData.get('city')==None:
        flash("Invalid Source or Destination", "error")
        return redirect(url_for('index'))
    date = [date.split('-')[2], date.split('-')[1], date.split('-')[0]]  # IN [DD, MM, YYYY]
    sessionId = generateId(source, destination)
    session[sessionId] = {"sourceData": sourceData, "destData": destData, "deptDate": date, "prefferedLang": prefferedLang}
    if sourceData['country'] == "India":
        return redirect(url_for('trainDetails', sessionId=sessionId))
    return redirect(url_for('flightDetails', sessionId=sessionId))

@app.route('/flight-details', methods=['GET','POST'])
def flightDetails():
    sessionId = request.args['sessionId']
    flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], session[sessionId]['destData']['city'], f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}")
    session[sessionId]['flightStatus'] = 'full'
    if flightData==[]:
        nearestAirport = location.nearestLocation(session[sessionId]['destData'])
        flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], nearestAirport, f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}")
        session[sessionId]['flightStatus'] = 'partial'
    data = {"sessionId": sessionId, "flightData": flightData, 'deptDate': f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"}
    return render_template('chooseFlight.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseFlight"]})

@app.route('/train-details', methods=['GET','POST'])
def trainDetails():
    sessionId = request.args['sessionId']
    src = session[sessionId]['sourceData']['city']
    dest = session[sessionId]['destData']['city']
    date = f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"
    if session[sessionId].get('flightStatus')!=None:
        session[sessionId]['flightData'] = json.loads(request.form['flightData'].replace("'", '"'))
        if session[sessionId]['flightStatus'] == 'full':
            return redirect(url_for('hotelDetails', sessionId=sessionId))
        else:
            src = session[sessionId]['flightData']["destination"]
            date = session[sessionId]['flightData']["arrivalDate"]
    trainData = train.getTrainDetails(src, dest, date)
    if trainData==[] or (not isinstance(trainData, list) and trainData.get('error')!=None):
        flash("No Train Available", "error")
        session.pop(sessionId)
        return redirect(url_for('index'))
    data = {"sessionId": sessionId,"src": src, "dest": dest, "deptDate": date, "trainData": trainData}
    return render_template('chooseTrain.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseTrain"]})

@app.route('/hotel-details', methods=['GET','POST'])
def hotelDetails():
    sessionId = request.args['sessionId']
    date = f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"
    if session[sessionId].get('flightStatus')!=None and session[sessionId].get('flightStatus') == 'full':
        date = session[sessionId]['flightData']["arrivalDate"]
    else:
        session[sessionId]['trainData'] = json.loads(request.form['trainData'].replace("'", '"'))
    date = [date.split('-')[0], date.split('-')[1], date.split('-')[2]]
    checkInDate = f"{date[2]}-{date[1]}-{date[0]}"
    checkOutDate = f"{date[2]}-{date[1]}-{str(int(date[0])+1)}"
    hotelData = hotel.getHotelDetails(session[sessionId]['destData']['city'], checkInDate, checkOutDate)
    if hotelData==[]:
        flash("No Hotel Available", "error")
        session.pop(sessionId)
        return redirect(url_for('index'))
    data = {"sessionId":sessionId, "hotelData": hotelData, "flightData": []}
    return render_template('chooseHotel.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseHotel"]})

@app.route('/trip-detail', methods=['GET','POST'])
def tripDetail():
    sessionId = request.args['sessionId']
    session[sessionId]['hotelData'] = json.loads(request.form['hotelData'].replace("'", '"'))
    data = [
            {
                "placeName": "From Vihar National Park",
                "description": "Van Vihar National Park is a popular tourist destination in Bhopal, known for its natural beauty and diverse wildlife. The park is home to a wide variety of animals, including tigers, leopards, bears, and various species of birds. Visitors can enjoy a safari through the park, or take a leisurely walk along the many trails. There are also several picnic areas and a children's playground.",
                "address": "Van Vihar Road, Bhopal, Madhya Pradesh 462003",
                "imageUrl": [
                    "https://bharatstories.com/wp-content/uploads/2016/02/Van-Vihar-National-Parkbhopal.jpg",
                    "https://gumlet.assettype.com/freepressjournal/2022-12/db7445ed-9c17-4321-9cac-610e88b4e460/van_vihar_national_park_bhopal__10_.jpg?rect=0%2C0%2C3900%2C2048&amp;w=1200&amp;auto=format%2Ccompress&amp;ogImage=true"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Van%20Vihar%20National%20Park%20Bhopal"
            },
            {
                "placeName": "Bhojtal",
                "description": "Bhojtal is a large lake located in the heart of Bhopal. The lake is a popular spot for boating, fishing, and bird watching. There are also several restaurants and cafes located along the shore of the lake. Visitors can enjoy a leisurely walk around the lake, or take a boat ride to explore the many islands.",
                "address": "Bhojtal, Bhopal, Madhya Pradesh 462038",
                "imageUrl": [
                    "https://c8.alamy.com/comp/H683E9/bhojtal-is-a-large-lake-which-lies-on-the-western-side-of-the-capital-H683E9.jpg",
                    "https://i.pinimg.com/originals/96/27/82/962782e4c922d828f91caf9eae176f00.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Bhojtal%20Bhopal"
            },
            {
                "placeName": "Upper Lake",
                "description": "The Upper Lake is a large lake located in the northern part of Bhopal. The lake is a popular spot for boating, fishing, and swimming. There are also several temples and mosques located along the shore of the lake. Visitors can enjoy a leisurely walk around the lake, or take a boat ride to explore the many islands.",
                "address": "Upper Lake, Bhopal, Madhya Pradesh 462003",
                "imageUrl": [
                    "https://www.wheelsonourfeet.com/wp-content/uploads/2016/02/Upper-Lake-in-Bhopal-1.jpg",
                    "https://www.trawell.in/admin/images/upload/145239155Upper-Lake.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Upper%20Lake%20Bhopal"
            },
            {
                "placeName": "Lower Lake",
                "description": "The Lower Lake is a small lake located in the southern part of Bhopal. The lake is a popular spot for boating, fishing, and swimming. There are also several temples and mosques located along the shore of the lake. Visitors can enjoy a leisurely walk around the lake, or take a boat ride to explore the many islands.",
                "address": "Lover Lake, Bhopal, Madhya Pradesh 462003",
                "imageUrl": [
                    "https://cdn1.goibibo.com/voy_ing/t_fs/bhopal-lower-lake-157387635624o.jpeg",
                    "https://images.herzindagi.info/image/2021/Jun/Bhopal-lake.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Lower%20Lake%20Bhopal"
            },
            {
                "placeName": "Taj-ul-Masjid",
                "description": "Taj-ul-Masjid is a large mosque located in the heart of Bhopal. The mosque is one of the largest mosques in India, and is a popular tourist destination. Visitors can admire the intricate architecture of the mosque, or take a guided tour to learn about its history.",
                "address": "Taj-ul-Masjid Road, Bhopal, Madhya Pradesh 462001",
                "imageUrl": [
                    "https://cdn.theculturetrip.com/wp-content/uploads/2016/04/tajul-masajid.jpeg",
                    "https://www.holidaytravel.co/uploaded_files/destination_img/2016_3857efa2d2e5b3bthe-tajul-masjid-bhopal-tourist-guide.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Taj-ul-Masjid%20Bhopal"
            },
            {
                "placeName": "Shaukat Mahal",
                "description": "Shaukat Mahal is a palace located in the heart of Bhopal. The palace was built in the 19th century, and is a popular tourist destination. Visitors can admire the intricate architecture of the palace, or take a guided tour to learn about its history.",
                "address": "Shaukat Mahal Road, Bhopal, Madhya Pradesh 462001",
                "imageUrl": [
                    "https://www.trawell.in/admin/images/upload/145239855Bhopal_Shaukat_Mahal_Main.jpg",
                    "https://www.hoteldekho.com/storage/img/tourattraction/1646731104Shaukat Mahal.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Shaukat%20Mahal%20Bhopal"
            },
            {
                "placeName": "Gohar Mahal",
                "description": "Gohar Mahal is a palace located in the heart of Bhopal. The palace was built in the 19th century, and is a popular tourist destination. Visitors can admire the intricate architecture of the palace, or take a guided tour to learn about its history.",
                "address": "Gauhar Mahal Road, Bhopal, Madhya Pradesh 462001",
                "imageUrl": [
                    "https://www.trawell.in/admin/images/upload/145239559Bhopal_Gohar_Mahal_Main.jpg",
                    "https://www.re-thinkingthefuture.com/wp-content/uploads/2020/06/A1008-Places-to-visit-in-Bhopal-for-the-Travelling-Architect-Gohar-Mahal-Image-1.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Gohar%20Mahal%20Bhopal"
            },
            {
                "placeName": "Human Museum.",
                "description": "Manav Sangrahalaya is a museum located in the heart of Bhopal. The museum is dedicated to the anthropology of India, and houses a large collection of artifacts from all over the country. Visitors can learn about the diverse cultures of India, and see how they have changed over time.",
                "address": "Manav Sangrahalaya Road, Bhopal, Madhya Pradesh 462003",
                "imageUrl": [
                    "https://www.tourismnewslive.com/wp-content/uploads/2018/04/odisha.jpg",
                    "https://holidify.com/images/attr_wiki/compressed/attr_wiki_3487.jpg",
                    "https://www.trawell.in/admin/images/upload/145239409Indiragandhimanav_sangrahalaya.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Manav%20Sangrahalaya%20Bhopal"
            },
            {
                "placeName": "Bhimbetka Caves",
                "description": "Bhimbetka Caves are a group of rock shelters located on the outskirts of Bhopal. The caves are home to a large number of prehistoric paintings, which date back to the Stone Age. Visitors can explore the caves, and see the paintings for themselves.",
                "address": "Bhimbetka Caves Road, Bhopal, Madhya Pradesh 462038",
                "imageUrl": [
                    "https://www.indiatravelblog.net/wp-content/uploads/2011/02/Bhimbetka-Caves.jpg",
                    "https://static.wixstatic.com/media/689c7e_001049cd7b65452abc356c32218db5a9~mv2.jpg/v1/fill/w_1000,h_500,al_c,q_90,usm_0.66_1.00_0.01/689c7e_001049cd7b65452abc356c32218db5a9~mv2.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Bhimbetka%20Caves%20Bhopal"
            },
            {
                "placeName": "Sanchi Stupa",
                "description": "Sanchi Stupa is a Buddhist stupa located on the outskirts of Bhopal. The stupa was built in the 3rd century BC, and is a popular tourist destination. Visitors can admire the intricate carvings on the stupa, or take a guided tour to learn about its history.",
                "address": "Sanchi Stupa Road, Bhopal, Madhya Pradesh 462038",
                "imageUrl": [
                    "https://www.holidify.com/images/cmsuploads/compressed/sanchistupa_20180219185128.jpg",
                    "https://www.esamskriti.com/essays/docfile/42_3746.jpg"
                ],
                "mapsDeeplink": "https://www.google.com/maps/search/?api=1&query=Sanchi%20Stupa%20Bhopal"
            }
        ]
    #data = languageData["content"][destinationData["city-en"]]
    data = {"sourceData": session[sessionId]['sourceData'], "destinationData": session[sessionId]['destData'], "deptDate": f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}", "hotelData": session[sessionId]['hotelData'], "guideDetails": db.guideDetails["en"], "content": data}
    if session[sessionId].get('flightData')!=None:
        data["flightData"] = session[sessionId]['flightData']
        if session[sessionId]['flightStatus'] == 'partial':
            data["trainData"] = session[sessionId]['trainData']
    else:
        data["trainData"] = session[sessionId]['trainData']
        searchFormat = (data["trainData"]["source"] + " Railway Station").replace(' ', '%20')
        data["trainData"]["mapsDeeplink"] = "https://www.google.com/maps/search/?api=1&query=" + searchFormat
    searchFormat = (data["hotelData"]["name"] + " " + data["destinationData"]["city"]).replace(' ', '%20')
    data["hotelData"]["mapsDeeplink"] = "https://www.google.com/maps/search/?api=1&query=" + searchFormat
    return render_template('chooseGuide.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseGuide"]})


def generateId(source, destination):
    return f"{str(round(time.time()*1000))}{source[:2]}{destination[:2]}"







if __name__ == "__main__":
    app.run()
