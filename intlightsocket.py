from flask import Flask
from flask_socketio import SocketIO
from message_manager import MessageManager

def start_int_lighting_service(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/int_lighting')
    def handle_internal_lighting():
        data = message_manager.get_data()
        return {"Internal": data["Internal"]}

    @socketio.on('connect')
    def handle_connect():
        print("Client connected to Internal Lighting Service")

    print(f"Internal Lighting Service running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)
