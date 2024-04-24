from flask_frozen import Freezer
from flask import Flask, render_template, send_file

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'content'
POST_DIR = 'posts'

app = Flask(__name__)

@app.route("/")

def home():
    return render_template("index.html")

@app.route("/download")
def download_file():
    filepath = "./outputs/output.csv"
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)