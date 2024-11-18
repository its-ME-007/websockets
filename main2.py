from gevent import monkey, spawn, joinall
monkey.patch_all()
from flask import Flask, render_template
from flask_socketio import SocketIO
from message_manager import MessageManager
from lighting_services import start_lighting_services
from bmssocket import start_bms_service
from tyresocket import start_tyre_service
import logging
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})

# Define allowed origins

socketio = SocketIO(
    app,
    async_mode='gevent',
    logger=True,
    engineio_logger=True,
    cors_allowed_origins="http://localhost:5000"
)

message_manager = MessageManager("can_data.json", socketio)

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

def create_default_json_if_not_exists(filename):
    if not os.path.exists(filename):
        default_data = {
            "Internal": {},
            "External": {},
            "Battery": {},
            "Tyre": {}
        }
        with open(filename, "w") as f:
            json.dump(default_data, f, indent=4)
        logging.info(f"Created default {filename}")
    else:
        logging.info(f"Using existing {filename}")

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting services...")

    create_default_json_if_not_exists("can_data.json")
    monitor = spawn(message_manager.monitor_updates)
    
    # Create green threads for all services, with lighting services on same port
    services = [
        spawn(start_lighting_services, 5001, message_manager),  # Both lighting services on port 5001
        spawn(start_bms_service, 5002, message_manager),        # Adjusted port numbers
        spawn(start_tyre_service, 5003, message_manager),       # Adjusted port numbers
    ]

    try:
        joinall([monitor] + services)
    except KeyboardInterrupt:
        logging.info("Shutting down services...")
    except Exception as e:
        logging.error(f"Error in services: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Application shutdown by user")
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
