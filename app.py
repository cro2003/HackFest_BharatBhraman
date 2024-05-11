from flask import Flask, request, render_template, redirect, url_for, flash
import database as db
import os
from dotenv import load_dotenv
import threading
from datetime import timedelta
import flight
import location
import train
import hotel
import json
import utils
import translators as ts


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
    sessionId = utils.generateId(source, destination)
    thread = threading.Thread(target=utils.contentGen, args=(destData["city"],))
    thread.start()
    currency = db.currency.get(sourceData['country_code'].upper())
    session[sessionId] = {"sourceData": sourceData, "destData": destData, "deptDate": date, "prefferedLang": prefferedLang, "currency": currency}
    if sourceData['country'] == "India":
        return redirect(url_for('trainDetails', sessionId=sessionId))
    return redirect(url_for('flightDetails', sessionId=sessionId))

@app.route('/flight-details', methods=['GET','POST'])
def flightDetails():
    sessionId = request.args['sessionId']
    flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], session[sessionId]['destData']['city'], f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}", session[sessionId]['currency'])
    session[sessionId]['flightStatus'] = 'full'
    if flightData==[]:
        nearestAirport = location.nearestLocation(session[sessionId]['destData'])
        flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], nearestAirport, f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}", session[sessionId]['currency'])
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
    currency = session[sessionId]['currency']
    date = f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"
    if session[sessionId].get('flightStatus')!=None:
        session[sessionId]['flightData'] = json.loads(request.form['flightData'].replace("'", '"'))
        if session[sessionId]['flightStatus'] == 'full':
            return redirect(url_for('hotelDetails', sessionId=sessionId))
        else:
            src = session[sessionId]['flightData']["destination"]
            date = session[sessionId]['flightData']["arrivalDate"]
    trainData = train.getTrainDetails(src, dest, date, currency)
    if trainData==[] or (not isinstance(trainData, list) and trainData.get('error')!=None):
        flash("No Train Available", "error")
        session.pop(sessionId)
        return redirect(url_for('index'))
    data = {"sessionId": sessionId,"src": src, "dest": dest, "deptDate": date, "trainData": trainData, "currency": currency}
    if session[sessionId].get('prefferedLang') != 'en':
        AcceptedKey = ['trainName', 'source', 'destination']
        cache_data = {}
        for traine in data['trainData']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language="hi")
                        cache_data[oldData] = traine[key]
                    else:
                        traine[key] = cache_data[traine[key]]
    return render_template('chooseTrain.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseTrain"]})

@app.route('/hotel-details', methods=['GET','POST'])
def hotelDetails():
    sessionId = request.args['sessionId']
    currency = session[sessionId]['currency']
    date = f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"
    if session[sessionId].get('flightStatus')!=None and session[sessionId].get('flightStatus') == 'full':
        date = session[sessionId]['flightData']["arrivalDate"]
    else:
        session[sessionId]['trainData'] = json.loads(request.form['trainData'].replace("'", '"'))
    date = [date.split('-')[0], date.split('-')[1], date.split('-')[2]]
    checkInDate = f"{date[2]}-{date[1]}-{date[0]}"
    checkOutDate = f"{date[2]}-{date[1]}-{str(int(date[0])+1)}"
    hotelData = hotel.getHotelDetails(session[sessionId]['destData']['city'], checkInDate, checkOutDate, currency)
    if hotelData==[]:
        flash("No Hotel Available", "error")
        session.pop(sessionId)
        return redirect(url_for('index'))
    data = {"sessionId":sessionId, "hotelData": hotelData, "currency": currency}
    return render_template('chooseHotel.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseHotel"]})

@app.route('/trip-detail', methods=['GET','POST'])
def tripDetail():
    sessionId = request.args['sessionId']
    session[sessionId]['hotelData'] = json.loads(request.form['hotelData'].replace("'", '"'))
    data = db.getContentData(session[sessionId]['destData']["city"])
    data = {"sourceData": session[sessionId]['sourceData'], "destinationData": session[sessionId]['destData'], "deptDate": f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}", "hotelData": session[sessionId]['hotelData'], "guideDetails": db.guideDetails["en"], "content": data, "currency": session[sessionId]['currency']}
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

@app.route('/guide', methods=['GET'])
def guide():
    data = db.getGuidePlace()
    print(data)
    data.pop(0)
    return render_template('guideIndex.html', data=data)

@app.route('/show-guide', methods=['POST'])
def showGuide():
    data = db.showGuide(request.form['name'])
    return render_template('guideresult.html', data=data)

@app.route('/add-guide', methods=['GET','POST'])
def addGuidePage():
    data = db.getGuidePlace()
    data.pop(0)
    return render_template("guideRegister.html", data=data)


@app.route('/get-guide', methods=['POST'])
def getGuide():
    guideName = request.form['first']
    guideAge = request.form['Age']
    guideGender = request.form['gender']
    guidePhoto = "URL"
    langKnown = request.form['Language']
    emailId = request.form['email']
    phoneNum = request.form['mobile']
    placeName = request.form['Toursist_Place']
    city = request.form['city']
    price = int(request.form['price']) + int(request.form['price'])*0.25
    data = {"guideName": guideName, "guideAge": guideAge, "guideGender": guideGender, "guidePhoto": guidePhoto, "langKnown": langKnown, "emailId": emailId, "phoneNum": phoneNum, "placeName": placeName, "city": city, "price": price}
    db.postGuideData(placeName, data)
    flash("Guide Added Successfully", "success")
    return redirect(url_for('addGuidePage'))




if __name__ == "__main__":
    app.run()