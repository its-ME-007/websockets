from flask import Flask
from flask_socketio import SocketIO
from message_manager import MessageManager

def start_bms_service(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/bms')
    def handle_bms():
        data = message_manager.get_data()
        return {"Battery": data["Battery"]}

    @socketio.on('connect')
    def handle_connect():
        print("Client connected to BMS Service")

    print(f"BMS Service running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)
