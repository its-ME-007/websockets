from flask import Flask
from flask_socketio import SocketIO
from message_manager import MessageManager

def start_ext_lighting_service(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/ext_lighting')
    def handle_external_lighting():
        data = message_manager.get_data()
        return {"External": data.get("External", {})}

    @socketio.on('connect')
    def handle_connect():
        print("Client connected to External Lighting Service")

    print(f"External Lighting Service running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)
