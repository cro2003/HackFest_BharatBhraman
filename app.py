from flask import Flask, request, render_template, session, redirect, url_for, flash
import database as db
import os
from dotenv import load_dotenv
from datetime import timedelta
import time
import requests
import flight

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)
LOCATION_API_KEY = os.environ.get('LOCATION')



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
    sourceData = getLocation(source)
    destData = getLocation(destination)
    if sourceData==[] or destData==[]:
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
    data = {"sourceData": session[sessionId]['sourceData'], "destinationData": session[sessionId]['destData'], "deptDate": f"{session[sessionId]['deptDate'][0]}-{session[sessionId]['deptDate'][1]}-{session[sessionId]['deptDate'][2]}",
            "flightData": flightData}
    return render_template('chooseFlight.html', data=data, supportedLanguage=db.languageData['supportedLanguages'],
                           pageLang={"language": session[sessionId]['prefferedLang'], "codeToLang": db.languageData["codeToLang"],
                                     "translatedData": db.languageData["translatedData"][session[sessionId]['prefferedLang']]["chooseFlight"]})

@app.route('/train-details', methods=['GET','POST'])
def trainDetails():
    return f"{request.args['sessionId']}"
def generateId(source, destination):
    return f"{str(round(time.time()*1000))}{source[:2]}{destination[:2]}"

def getLocation(query):
    response = requests.get(
        f"https://api.geoapify.com/v1/geocode/search?text={query}&format=json&apiKey={LOCATION_API_KEY}", ).json()[
        'results']
    if response == []:
        return []
    return response[0]



if __name__ == "__main__":
    app.run()
