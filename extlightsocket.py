import json
import time
from flask import render_template, Blueprint
from socketio_instance import socketio  

ext_lighting_bp = Blueprint("extlightsocket", __name__)
STATUS_FILE_PATH = 'ext_status.json'
last_status = None  # Keep track of the last status to detect changes
current_status = None  # Store the currently loaded status in memory

def load_external_lighting_status():
    """Load the external lighting status from the JSON file."""
    global current_status
    try:
        with open(STATUS_FILE_PATH, 'r') as file:
            current_status = json.load(file)
    except FileNotFoundError:
        current_status = {"External": {}}

def status_to_string(status_value):
    """Convert the status value to a string ("OFF" for 0, "ON" for 1)."""
    return "ON" if status_value == 1 else "OFF"

def broadcast_external_updates():
    """Continuously check for updates in the JSON file and broadcast them."""
    global last_status
    while True:
        if current_status != last_status:
            last_status = current_status.copy()  # Track the new status
            # Convert status values and broadcast to all connected clients
            socketio.emit('headlights_status', {"HeadlightsStatus": status_to_string(current_status["External"].get("Headlights", {}).get("Status", 0))})
            socketio.emit('taillights_status', {"TailLightsStatus": status_to_string(current_status["External"].get("TailLights", {}).get("Status", 0))})
            socketio.emit('brakelights_status', {"BrakeLightsStatus": status_to_string(current_status["External"].get("BrakeLights", {}).get("Status", 0))})
            socketio.emit('turnsignals_status', {"TurnSignalsStatus": status_to_string(current_status["External"].get("TurnSignals", {}).get("Status", 0))})
            socketio.emit('foglights_status', {"FogLightsStatus": status_to_string(current_status["External"].get("FogLights", {}).get("Status", 0))})
        time.sleep(1)  # Check every 10 seconds

# Serve the HTML template
@ext_lighting_bp.route('/')
def index():
    return render_template('index_extlighting.html')
