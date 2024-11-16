import threading
from flask import Flask
from socketio_instance import socketio
from intlightsocket import int_lighting_bp, socketio, load_internal_lighting_status, broadcast_internal_updates
from extlightsocket import ext_lighting_bp, load_external_lighting_status, broadcast_external_updates ,socketio

app = Flask(__name__)
socketio.init_app(app)  # Initialize SocketIO with the Flask app

# Register the int_lighting blueprint
app.register_blueprint(int_lighting_bp, url_prefix='/int_lighting')
app.register_blueprint(ext_lighting_bp, url_prefix='/ext_lighting')

# Start a thread to run the broadcast_updates function
def start_broadcast_thread():
    load_internal_lighting_status()
    load_external_lighting_status()

    int_light_thread = threading.Thread(target=broadcast_internal_updates,daemon = True)
    ext_light_thread = threading.Thread(target=broadcast_external_updates)

    int_light_thread.start()
    ext_light_thread.start()

if __name__ == "__main__":
    start_broadcast_thread()
    socketio.run(app, debug=True)
