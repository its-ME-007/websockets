from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define allowed origins
allowed_origins = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5002",
    "http://localhost:5003",
    "http://localhost:5004",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5004"
]

socketio = SocketIO(
    app,
    cors_allowed_origins=allowed_origins,
    async_mode='gevent',
    logger=True,
    engineio_logger=True
)

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 
