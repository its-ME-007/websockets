import json
import time
from flask import render_template, Blueprint
from socketio_instance import socketio  

int_lighting_bp = Blueprint ('intlightsocket',__name__)
STATUS_FILE_PATH = 'can_data.json'
last_status = None  # Keep track of the last status to detect changes
current_status = None  # Store the currently loaded status in memory

def load_internal_lighting_status():
    """Load the internal lighting status from the JSON file."""
    global current_status
    try:
        with open(STATUS_FILE_PATH, 'r') as file:
            current_status = json.load(file)
    except FileNotFoundError:
        current_status = {"Internal": {}}

def broadcast_internal_updates():
    """Continuously check for updates in the JSON file and broadcast them."""
    global last_status
    while True:
        # Only broadcast if the status has changed
        if current_status != last_status:
            last_status = current_status.copy()  # Keep track of the new status
            # Broadcast each lighting status to all connected clients
            socketio.emit('rooflight_status', {"RoofLightStatus": current_status["Internal"].get("RoofLight", {}).get("Status", 0)})
            socketio.emit('rooflight_brightness', {"RoofLightBrightness": current_status["Internal"].get("RoofLight", {}).get("Brightness", 0)})
            socketio.emit('doorpuddlelights_status', {"DoorPuddleLightsStatus": current_status["Internal"].get("DoorPuddleLights", {}).get("Status", 0)})
            socketio.emit('doorpuddlelights_brightness', {"DoorPuddleLightsBrightness": current_status["Internal"].get("DoorPuddleLights", {}).get("Brightness", 0)})
            socketio.emit('floorlights_status', {"FloorLightsStatus": current_status["Internal"].get("FloorLights", {}).get("Status", 0)})
            socketio.emit('floorlights_brightness', {"FloorLightsBrightness": current_status["Internal"].get("FloorLights", {}).get("Brightness", 0)})
            socketio.emit('dashboardlights_status', {"DashboardLightsStatus": current_status["Internal"].get("DashboardLights", {}).get("Status", 0)})
            socketio.emit('dashboardlights_brightness', {"DashboardLightsBrightness": current_status["Internal"].get("DashboardLights", {}).get("Brightness", 0)})
            socketio.emit('bootlights_status', {"BootLightsStatus": current_status["Internal"].get("BootLights", {}).get("Status", 0)})
        time.sleep(0.5)  

# Serve the HTML template
@int_lighting_bp.route('/')
def index():
    return render_template('index_lighting.html')
