from flask import Flask, request, render_template
import database as db

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    defaultLang = "en"
    if request.method=='POST':
        defaultLang = request.form['selectedLang']
    return render_template('index.html', supportedLanguage = db.languageData['supportedLanguages'], pageLang = {"language": defaultLang, "codeToLang":  db.languageData["codeToLang"], "translatedData": db.languageData["translatedData"][defaultLang]["index"]})

if __name__ == "__main__":
    app.run()
