from flask_socketio import SocketIO
# Create a shared SocketIO instance
socketio = SocketIO(async_mode='gevent')  