from flask import Flask, render_template, send_file, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = "./uploads" # TODO use pathlib instead
OUTPUT_FOLDER = "./outputs"
ALLOWED_EXTENSIONS = {'pdf', 'json'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def upload():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    uploaded_files = request.files.getlist("files[]")

    for file in uploaded_files:
        if file.filename == "":
            return "No files selected"
        if not allowed_file(file.filename):
            return "File format should be PDF"
        
        file.save("uploads/" + file.filename)

    return "Upload successful!"

@app.route("/download")
def download_file():
    path = "output.csv"
    filename = app.config['OUTPUT_FOLDER'] + "/" + path
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)