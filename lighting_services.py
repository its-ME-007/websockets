from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO
from message_manager import MessageManager

def start_lighting_services(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/int_lighting')
    def handle_internal_lighting():
        data = message_manager.get_data()
        return {"Internal": data["Internal"]}

    @app.route('/ext_lighting')
    def handle_external_lighting():
        data = message_manager.get_data()
        return {"External": data["External"]}

    @socketio.on('connect')
    def handle_connect():
        print("Client connected to Lighting Service")

    print(f"Lighting Services running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port) 