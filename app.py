


from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from datetime import datetime
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# === MongoDB Setup ===
client = MongoClient("mongodb+srv://pdf2word:pdf2word@pdf2word.rk8udig.mongodb.net/?retryWrites=true&w=majority&appName=pdf2word")
db = client["pdf2word_db"]
files_collection = db["converted_files"]

# === Upload Endpoint ===
@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    return jsonify({'filename': unique_name})

# === Convert Endpoint ===
@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = filename.replace('.pdf', '.docx')
    output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

    # Use pdf2docx (or your method) here
    from pdf2docx import Converter
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

    # Save metadata to MongoDB
    files_collection.insert_one({
        "original_filename": filename,
        "converted_filename": output_filename,
        "upload_date": datetime.utcnow(),
        "status": "converted"
    })

    return jsonify({'download_url': f'/download/{output_filename}'})

# === Download Endpoint ===
@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(os.path.join(app.config['CONVERTED_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
