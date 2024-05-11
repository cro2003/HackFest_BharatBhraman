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
    if session[sessionId].get('flightStatus')!=None:
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
    data = {"hotelData": hotelData, "flightData": []}
    return render_template('chooseHotel.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseHotel"]})

def generateId(source, destination):
    return f"{str(round(time.time()*1000))}{source[:2]}{destination[:2]}"







if __name__ == "__main__":
    app.run()
