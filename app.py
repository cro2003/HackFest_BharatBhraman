import time
import genai
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
    session[sessionId] = {"sourceData": sourceData, "destData": destData, "deptDate": date, "prefferedLang": prefferedLang, "currency": currency, "sessionId": sessionId}
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
    if session[sessionId].get('prefferedLang') != 'en':
        AcceptedKey = ['flightName', 'src', 'destination']
        cache_data = {}
        for traine in data['flightData']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = traine[key]
                    else:
                        traine[key] = cache_data[traine[key]]
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
        if cache_data.get(data['src']) is None:
            data['src'] = ts.translate_text(data['src'], from_language="en", to_language=session[sessionId].get('prefferedLang'))
        else:
            data['src'] = cache_data[data['src']]
        if cache_data.get(data['dest']) is None:
            data['dest'] = ts.translate_text(data['dest'], from_language="en", to_language=session[sessionId].get('prefferedLang'))
        else:
            data['dest'] = cache_data[data['dest']]
        for traine in data['trainData']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
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
    if session[sessionId].get('prefferedLang') != 'en':
        AcceptedKey = ['name', 'location']
        cache_data = {}
        for traine in data['hotelData']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = traine[key]
                    else:
                        traine[key] = cache_data[traine[key]]
    return render_template('chooseHotel.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseHotel"]})

@app.route('/trip-detail', methods=['GET','POST'])
def tripDetail():
    try:
        sessionId = request.args['sessionId']
        session[sessionId]['hotelData'] = json.loads(request.form['hotelData'].replace("'", '"'))
    except:
        sessionId = request.form['sessionId']
        session[sessionId]['prefferedLang'] = request.form['selectedLang']
    data = db.getContentData(session[sessionId]['destData']["city"])
    data = {"sourceData": session[sessionId]['sourceData'], "destinationData": session[sessionId]['destData'], "deptDate": f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}", "hotelData": session[sessionId]['hotelData'], "guideDetails": db.guideDetails["en"], "content": data, "currency": session[sessionId]['currency'], "sessionid": sessionId}
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
    data["sessionId"] = sessionId
    if session[sessionId].get('prefferedLang') != 'en':
        AcceptedKey = ['placeName', 'description', 'address', 'name', 'location', 'trainName', 'source', 'flightName', 'src', 'destination']
        cache_data = {}
        for traine in data['content']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = traine[key]
                    else:
                        traine[key] = cache_data[traine[key]]
        for key in data["hotelData"].keys():
            if key in AcceptedKey:
                if cache_data.get(data["hotelData"][key]) is None:
                    oldData = data["hotelData"][key]
                    data["hotelData"][key] = ts.translate_text(data["hotelData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                    cache_data[oldData] = data["hotelData"][key]
                else:
                    data["hotelData"][key] = cache_data[data["hotelData"][key]]
        if session[sessionId].get('flightData') != None:
            for key in data["flightData"].keys():
                if key in AcceptedKey:
                    if cache_data.get(data["flightData"][key]) is None:
                        oldData = data["flightData"][key]
                        data["flightData"][key] = ts.translate_text(data["flightData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = data["flightData"][key]
                    else:
                        data["flightData"][key] = cache_data[data["flightData"][key]]
        if session[sessionId].get('trainData') != None:
            for key in data["trainData"].keys():
                if key in AcceptedKey:
                    if cache_data.get(data["trainData"][key]) is None:
                        oldData = data["trainData"][key]
                        data["trainData"][key] = ts.translate_text(data["trainData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = data["trainData"][key]
                    else:
                        data["trainData"][key] = cache_data[data["trainData"][key]]
    return render_template('chooseGuide.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseGuide"]})

@app.route('/quick-pick', methods=['POST'])
def quickPicks():
    prefferedLang = request.form['selectedLang'].strip()
    source = request.form['from']
    destination = request.form['to']
    prfrnce = request.form['select']
    date = request.form['date']
    sourceData = location.getLocation(source)
    destData = location.getLocation(destination)
    if sourceData == [] or destData == [] or destData.get('city') == None or sourceData.get('city') == None:
        flash("Invalid Source or Destination", "error")
        return redirect(url_for('index'))
    date = [date.split('-')[2], date.split('-')[1], date.split('-')[0]]  # IN [DD, MM, YYYY]
    sessionId = utils.generateId(source, destination)
    thread = threading.Thread(target=utils.contentGen, args=(destData["city"],))
    thread.start()
    currency = db.currency.get(sourceData['country_code'].upper())
    session[sessionId] = {"sourceData": sourceData, "destData": destData, "deptDate": date,
                          "prefferedLang": prefferedLang, "currency": currency, "sessionId": sessionId}
    if prfrnce == "Comfort":
        flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'],
                                             session[sessionId]['destData']['city'],
                                             f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}",
                                             session[sessionId]['currency'])
        session[sessionId]['flightStatus'] = 'full'
        if flightData == []:
            nearestAirport = location.nearestLocation(session[sessionId]['destData'])
            flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], nearestAirport,
                                                 f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}",
                                                 session[sessionId]['currency'], 'comfort')
            session[sessionId]['flightStatus'] = 'partial'
            if flightData==[]:
                flash("No Flights Available", "error")
                session.pop(sessionId)
                return redirect(url_for('index'))
            session[sessionId]['flightData'] = flightData[0]
            src = session[sessionId]['flightData']["destination"]
            date = session[sessionId]['flightData']["arrivalDate"]
            trainData = train.getTrainDetails(src, session[sessionId]['destData']['city'], date, currency, 'comfort')
            if trainData==[]:
                flash("No Trains Available", "error")
                session.pop(sessionId)
                return redirect(url_for('index'))
            session[sessionId]['trainData'] = trainData[0]
        session[sessionId]['flightData'] = flightData[0]
        if session[sessionId].get('flightStatus') != None and session[sessionId].get('flightStatus') == 'full':
            date = session[sessionId]['flightData']["arrivalDate"]
        date = [date.split('-')[0], date.split('-')[1], date.split('-')[2]]
        checkInDate = f"{date[2]}-{date[1]}-{date[0]}"
        checkOutDate = f"{date[2]}-{date[1]}-{str(int(date[0]) + 1)}"
        hotelData = hotel.getHotelDetails(session[sessionId]['destData']['city'], checkInDate, checkOutDate, currency, 'comfort')
        session[sessionId]['hotelData'] = hotelData[0]
    else:
        if sourceData['country'] == "India":
            src = session[sessionId]['sourceData']['city']
            dest = session[sessionId]['destData']['city']
            date = f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}"
            trainData = train.getTrainDetails(src, dest, date, currency, 'budget')
            if trainData==[]:
                flash("No Trains Available", "error")
                session.pop(sessionId)
                return redirect(url_for('index'))
            session[sessionId]['trainData'] = trainData[0]
        else:
            flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'],
                                                 session[sessionId]['destData']['city'],
                                                 f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}",
                                                 session[sessionId]['currency'])
            session[sessionId]['flightStatus'] = 'full'
            if flightData == []:
                nearestAirport = location.nearestLocation(session[sessionId]['destData'])
                flightData = flight.getFlightDetails(session[sessionId]['sourceData']['city'], nearestAirport,
                                                     f"{session[sessionId]['deptDate'][0]}/{session[sessionId]['deptDate'][1]}/{session[sessionId]['deptDate'][2]}",
                                                     session[sessionId]['currency'])
                session[sessionId]['flightStatus'] = 'partial'
                if flightData == []:
                    flash("No Flights Available", "error")
                    session.pop(sessionId)
                    return redirect(url_for('index'))
                session[sessionId]['flightData'] = flightData[0]
                src = session[sessionId]['flightData']["destination"]
                date = session[sessionId]['flightData']["arrivalDate"]
                trainData = train.getTrainDetails(src, session[sessionId]['destData']['city'], date, currency, 'budget')
                if trainData == []:
                    flash("No Trains Available", "error")
                    session.pop(sessionId)
                    return redirect(url_for('index'))
                session[sessionId]['trainData'] = trainData[0]
            session[sessionId]['flightData'] = flightData[0]
        if session[sessionId].get('flightStatus') != None and session[sessionId].get('flightStatus') == 'full':
            date = session[sessionId]['flightData']["arrivalDate"]
        date = [date.split('-')[0], date.split('-')[1], date.split('-')[2]]
        checkInDate = f"{date[2]}-{date[1]}-{date[0]}"
        checkOutDate = f"{date[2]}-{date[1]}-{str(int(date[0]) + 1)}"
        hotelData = hotel.getHotelDetails(session[sessionId]['destData']['city'], checkInDate, checkOutDate, currency)
        session[sessionId]['hotelData'] = hotelData[0]
    data = db.getContentData(session[sessionId]['destData']["city"])
    if data==None:
        time.sleep(10)
    data = {"sourceData": session[sessionId]['sourceData'], "destinationData": session[sessionId]['destData'],
            "deptDate": f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}",
            "hotelData": session[sessionId]['hotelData'], "guideDetails": db.guideDetails["en"], "content": data,
            "currency": session[sessionId]['currency'], "sessionid": sessionId}
    if session[sessionId].get('flightData') != None:
        data["flightData"] = session[sessionId]['flightData']
        if session[sessionId]['flightStatus'] == 'partial':
            data["trainData"] = session[sessionId]['trainData']
    else:
        data["trainData"] = session[sessionId]['trainData']
        searchFormat = (data["trainData"]["source"] + " Railway Station").replace(' ', '%20')
        data["trainData"]["mapsDeeplink"] = "https://www.google.com/maps/search/?api=1&query=" + searchFormat
    searchFormat = (data["hotelData"]["name"] + " " + data["destinationData"]["city"]).replace(' ', '%20')
    data["hotelData"]["mapsDeeplink"] = "https://www.google.com/maps/search/?api=1&query=" + searchFormat
    data["sessionId"] = sessionId
    if session[sessionId].get('prefferedLang') != 'en':
        AcceptedKey = ['placeName', 'description', 'address', 'name', 'location', 'trainName', 'source', 'flightName', 'src', 'destination']
        cache_data = {}
        for traine in data['content']:
            for key in traine.keys():
                if key in AcceptedKey:
                    if cache_data.get(traine[key]) is None:
                        oldData = traine[key]
                        traine[key] = ts.translate_text(traine[key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = traine[key]
                    else:
                        traine[key] = cache_data[traine[key]]
        for key in data["hotelData"].keys():
            if key in AcceptedKey:
                if cache_data.get(data["hotelData"][key]) is None:
                    oldData = data["hotelData"][key]
                    data["hotelData"][key] = ts.translate_text(data["hotelData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                    cache_data[oldData] = data["hotelData"][key]
                else:
                    data["hotelData"][key] = cache_data[data["hotelData"][key]]
        if session[sessionId].get('flightData') != None:
            for key in data["flightData"].keys():
                if key in AcceptedKey:
                    if cache_data.get(data["flightData"][key]) is None:
                        oldData = data["flightData"][key]
                        data["flightData"][key] = ts.translate_text(data["flightData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = data["flightData"][key]
                    else:
                        data["flightData"][key] = cache_data[data["flightData"][key]]
        if session[sessionId].get('trainData') != None:
            for key in data["trainData"].keys():
                if key in AcceptedKey:
                    if cache_data.get(data["trainData"][key]) is None:
                        oldData = data["trainData"][key]
                        data["trainData"][key] = ts.translate_text(data["trainData"][key], from_language="en", to_language=session[sessionId].get('prefferedLang'))
                        cache_data[oldData] = data["trainData"][key]
                    else:
                        data["trainData"][key] = cache_data[data["trainData"][key]]
    return render_template('chooseGuide.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'],
                                     "codeToLang": db.languageData["codeToLang"],
                                     "translatedData":
                                         db.languageData["translatedData"][session[sessionId]['prefferedLang']][
                                             "chooseGuide"]})


@app.route('/guide', methods=['GET'])
def guide():
    data = db.getGuidePlace()
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

@app.route('/chat', methods=['GET'])
def chat():
    defaultLang = 'en'
    return render_template('chatBot.html', supportedLanguage = db.languageData['supportedLanguages'], pageLang = {"language": defaultLang, "codeToLang":  db.languageData["codeToLang"], "translatedData": db.languageData["translatedData"][defaultLang]["index"]})

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    lang = request.args.get('lang')
    text = genai.chatbotResponse(userText)
    if lang==None:
        lang = "en"
    if lang!='en':
        text = ts.translate_text(text, to_language=lang)
    return text

@app.route("/save-trip", methods=['POST'])
def saveTrip():
    sessionId = request.form['sessionId']
    db.saveTripData(session[sessionId])
    flash("Trip Saved Successfully", "success")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()