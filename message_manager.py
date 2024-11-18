import json
from threading import Lock
from flask_socketio import SocketIO
import logging
import time

class MessageManager:
    def __init__(self, file_path, socketio: SocketIO):
        self.file_path = file_path
        self.socketio = socketio
        self.data_cache = None
        self.lock = Lock()
        logging.basicConfig(level=logging.INFO)
        
    def get_data(self):
        """Get the current data from cache or file"""
        if self.data_cache is None:
            self.data_cache = self.read_file()
        return self.data_cache

    def read_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                if data != self.data_cache:
                    logging.info("Data updated in file")
                return data
        except Exception as e:
            logging.error(f"Error reading {self.file_path}: {str(e)}")
            return {
                "Internal": {},
                "External": {},
                "Battery": {},
                "Tyre": {}
            }

    def monitor_updates(self):
        logging.info(f"Starting to monitor {self.file_path}")
        while True:
            try:
                with self.lock:
                    new_data = self.read_file()
                    if new_data != self.data_cache:
                        logging.info("Broadcasting updated data")
                        self.data_cache = new_data
                        self.broadcast_updates()
                time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Monitor stopped")
                break
            except Exception as e:
                logging.error(f"Error in monitor: {str(e)}")
                time.sleep(1)

    def broadcast_updates(self):
        if self.socketio:  # Check if socketio is initialized
            for category, data in self.data_cache.items():
                category_event = category.lower()
                self.socketio.emit(category_event, data)  # Broadcast category data
