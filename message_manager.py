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
        self.valid_ranges = {
            "cell_voltage": (2.0, 4.2),  # Standard Li-ion cell voltage range
            "soc": (20, 100),  # From valid_ranges
            "tyre_pressure": (28, 35)  # Valid tyre pressure range in PSI
        }
        
    def get_data(self):
        """Get the current data from cache or file"""
        if self.data_cache is None:
            self.data_cache = self.read_file()
        return self.data_cache

    def read_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                if not self.validate_battery_data(data) or not self.validate_tyre_data(data):
                    logging.error("Invalid data detected")
                    return self.data_cache or {
                        "Internal": {},
                        "External": {},
                        "Battery": {},
                        "Tyre": {}
                    }
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
        if self.socketio:
            for category, data in self.data_cache.items():
                category_event = category.lower()
                self.socketio.emit(category_event, data)

    def validate_battery_data(self, data):
        """Validate battery data against defined ranges"""
        if "Battery" not in data:
            return False
        
        battery = data["Battery"]
        
        # Validate SOC
        if not (self.valid_ranges["soc"][0] <= battery.get("SOC", 0) <= self.valid_ranges["soc"][1]):
            logging.warning(f"SOC value {battery.get('SOC')} outside valid range {self.valid_ranges['soc']}")
            return False
        
        # Validate all cell voltages
        for i in range(1, 25):
            voltage_key = f"Voltage_{i}"
            voltage = battery.get(voltage_key, 0)
            if not (self.valid_ranges["cell_voltage"][0] <= voltage <= self.valid_ranges["cell_voltage"][1]):
                logging.warning(f"{voltage_key} value {voltage} outside valid range {self.valid_ranges['cell_voltage']}")
                return False
        
        return True

    def validate_tyre_data(self, data):
        """Validate tyre pressure data against defined ranges"""
        if "Tyre" not in data:
            return False
        
        tyre = data["Tyre"]
        tyre_positions = ["Right_Front", "Right_Back", "Left_Front", "Left_Back"]
        
        for position in tyre_positions:
            pressure = tyre.get(position, 0)
            if not (self.valid_ranges["tyre_pressure"][0] <= pressure <= self.valid_ranges["tyre_pressure"][1]):
                logging.warning(f"Tyre pressure for {position} value {pressure} outside valid range {self.valid_ranges['tyre_pressure']}")
                return False
        
        return True
