from flask import Flask, request, jsonify, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
import json

from main import start_neural_network

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Equipment_types = [
    'truck',
    'excavator',
    'tractor',
    'lifting_crane'
]

BackgroundColor = [
    'rgba(255, 99, 132, 0.2)',
    'rgba(54, 162, 235, 0.2)',
    'rgba(255, 206, 86, 0.2)',
    'rgba(75, 192, 192, 0.2)',
    'rgba(153, 102, 255, 0.2)',
    'rgba(255, 159, 64, 0.2)',
]

BorderColor = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
]

@app.route('/report')
def generate_report():
    file_path = 'data.json'
    
    return send_file(file_path, as_attachment=True)

@app.route('/chart-data', methods=['GET'])
def get_chart_data():
    chart_data = []

    if os.path.getsize("data.json") > 3:
        with open('data.json') as file:
            data = json.load(file)

            for equipment, events in data.items():
                label = equipment.split()[0].capitalize()
                equipment_type = "EquipmentTypes." + label
                data_list = [event["event_id"] for event in events]
                backgroundColor = BackgroundColor[Equipment_types.index(equipment.split()[0])]
                borderColor = BorderColor[Equipment_types.index(equipment.split()[0])]
                item = {
                    "label": equipment_type,
                    "data": data_list,
                    "backgroundColor": backgroundColor,
                    "borderColor": borderColor,
                    "borderWidth": 1
                }
                chart_data.append(item)

    return jsonify(chart_data)

@app.route('/table', methods=['GET'])
def get_table_data():
    table = []

    if os.path.getsize("data.json") > 3:
        with open('data.json') as file:
            data = json.load(file)
            for key, items in data.items():
                transport_type = key.split()[0].upper()
                for item in items:
                    event_id = item['event_id']
                    time = item['time']
                    time_end = item['time_end']
                    transport_name = transport_type
                    event = item['event']
                    coords = item['coords']
                    
                    new_item = {
                        'event_id': event_id,
                        'time': time,
                        'time_end': time_end,
                        'transport_name': transport_name,
                        'event': event,
                        'coords': coords
                    }
                
                    table.append(new_item)

    return jsonify(table)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        start_neural_network(filepath)
        resultname = filename.replace('.mp4', '') + '_result.mp4'
        os.remove(filepath)

        return jsonify({'path': resultname.replace('\\', '/')}), 200

    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/uploads/<path:filename>')
def serve_video(filename):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']), filename)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run()
