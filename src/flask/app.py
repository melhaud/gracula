#from flask_frozen import Freezer
from flask import Flask, render_template, send_file
import json

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'content'
POST_DIR = 'posts'

app = Flask(__name__)

@app.route("/")

def index():
    with open("settings.txt", encoding="utf8") as base_config:
        data = base_config.read()
        settings = json.loads(data)

    # variables = {
    #     "title" : "Gracula Project",
    #     "description" : "Gracula🧛‍♂️🧛‍♀️ is an AI-agent-based scientific papers extractor. It uses GigaChat API to analyse user-uploaded PDF files and build a compilation table dataset out of them.",
    #     "keywords" : "scientific parser, gigachat"
    # }
    return render_template("index.html", bigheader=True, **settings)

@app.route("/download")
def download_file():
    filepath = "./outputs/output.csv"
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
