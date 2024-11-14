import json
import time
import threading
from flask import Blueprint
from flask_socketio import SocketIO, emit

ext_lighting_bp = Blueprint('ext_lighting', __name__)
socketio = SocketIO()
STATUS_FILE_PATH = 'can_data.json'
last_status, current_status = None, None

def load_external_lighting_status():
    global current_status
    try:
        with open(STATUS_FILE_PATH, 'r') as file:
            current_status = json.load(file)
    except FileNotFoundError:
        current_status = {"External": {}}

def status_to_string(status_value):
    return "ON" if status_value == 1 else "OFF"

def broadcast_external_updates():
    global last_status
    while True:
        if current_status != last_status:
            last_status = current_status.copy()
            socketio.emit('headlights_status', {"HeadlightsStatus": status_to_string(current_status["External"].get("Headlights", {}).get("Status", 0))})
            socketio.emit('taillights_status', {"TailLightsStatus": status_to_string(current_status["External"].get("TailLights", {}).get("Status", 0))})
            socketio.emit('brakelights_status', {"BrakeLightsStatus": status_to_string(current_status["External"].get("BrakeLights", {}).get("Status", 0))})
            socketio.emit('turnsignals_status', {"TurnSignalsStatus": status_to_string(current_status["External"].get("TurnSignals", {}).get("Status", 0))})
            socketio.emit('foglights_status', {"FogLightsStatus": status_to_string(current_status["External"].get("FogLights", {}).get("Status", 0))})
        time.sleep(10)

def init_ext_lighting(socket_io_instance):
    global socketio
    socketio = socket_io_instance
    load_external_lighting_status()
    threading.Thread(target=broadcast_external_updates, daemon=True).start()
