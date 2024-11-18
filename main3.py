import gevent
from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO
from intlightsocket import int_lighting_bp, load_internal_lighting_status, broadcast_internal_updates
from extlightsocket import ext_lighting_bp, load_external_lighting_status, broadcast_external_updates 
from bmssocket import bms_bp, load_battery_status, broadcast_bms_updates 
from tyresocket import tyre_bp, load_tyre_status, broadcast_tp_updates

app_lighting = Flask(__name__)
app_bms = Flask(__name__)
app_tyre = Flask(__name__)
socketio_ext = SocketIO(app_lighting, async_mode='gevent')
socketioint = SocketIO(app_lighting, async_mode='gevent')
socketio_bms = SocketIO(app_bms, async_mode='gevent')
socketio_tyre = SocketIO(app_tyre, async_mode='gevent')

# Register the blueprint
app_lighting.register_blueprint(ext_lighting_bp, url_prefix='/ext_lighting')
app_lighting.register_blueprint(int_lighting_bp, url_prefix='/int_lighting')
app_bms.register_blueprint(bms_bp, url_prefix='/bms')
app_tyre.register_blueprint(tyre_bp, url_prefix='/tyre_pressure')

# Define a basic route for SocketIO
@app_lighting.route('/')
def handle_lighting_events():
    pass

@app_bms.route('/')
def handle_bms_events():
    pass

@app_tyre.route('/')
def handle_tyre_events():
    pass 

def start_lighting_broadcast():
    load_external_lighting_status()
    load_internal_lighting_status()
    broadcast_external_updates()  
    broadcast_internal_updates()

def start_lighting_server(port):
    def run_server():
        start_lighting_broadcast()
        socketio_ext.run(app_lighting, host='0.0.0.0', port=port)
    gevent.spawn(run_server)

def start_bms_broadcast():
    load_battery_status()
    broadcast_bms_updates()

def start_bms_server(port):
    def run_server():
        start_bms_broadcast()
        socketio_ext.run(app_bms, host='0.0.0.0', port=port)
    gevent.spawn(run_server)

def start_tp_broadcast():
    load_tyre_status()
    broadcast_tp_updates()

def start_tyre_pressure_server(port):
    def run_server():
        start_tp_broadcast()
        socketio_ext.run(app_tyre, host='0.0.0.0', port=port)
    gevent.spawn(run_server)

if __name__ == "__main__":
    start_bms_server(5001)
    start_lighting_server(5002) 
    start_tyre_pressure_server(5003)
    # Start other servers for BMS, tyre pressure, etc.