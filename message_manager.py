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
            "cell_voltage": (60,85),  # Standard Li-ion cell voltage range
            "soc": (20, 100),  # From valid_ranges
            "tyre_pressure": (28, 35),  # Valid tyre pressure range in PSI
            "heartbeat": (0, 1)  # Valid heartbeat values
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
                battery_valid, battery_msg, battery_code = self.validate_battery_data(data)
                tyre_valid, tyre_msg, tyre_code = self.validate_tyre_data(data)
                ecu_valid, ecu_msg, ecu_code = self.validate_ecu_data(data)
                
                if not battery_valid or not tyre_valid or not ecu_valid:
                    logging.error("Invalid data detected")
                    error_data = data.copy() if data else {}
                    error_data['_validation_errors'] = {
                        'battery': {
                            'valid': battery_valid,
                            'message': battery_msg,
                            'code': battery_code
                        },
                        'tyre': {
                            'valid': tyre_valid,
                            'message': tyre_msg,
                            'code': tyre_code
                        },
                        'ecu': {
                            'valid': ecu_valid,
                            'message': ecu_msg,
                            'code': ecu_code
                        },
                        'timestamp': time.time()
                    }
                    return error_data
                
                if data != self.data_cache:
                    logging.info("Data updated in file")
                return data
        except Exception as e:
            logging.error(f"Error reading {self.file_path}: {str(e)}")
            return {
                "Internal": {},
                "External": {},
                "Battery": {},
                "Tyre": {},
                "LEVEL2_CU": {},
                "_validation_errors": {
                    "file_error": str(e),
                    "timestamp": time.time(),
                    "code": 500
                }
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
            if '_validation_errors' in self.data_cache:
                # Emit an error event with detailed validation information
                self.socketio.emit('validation_error', self.data_cache['_validation_errors'])
                logging.error(f"Validation errors detected: {self.data_cache['_validation_errors']}")
            
            for category, data in self.data_cache.items():
                if not category.startswith('_'):  # Skip internal fields
                    category_event = category.lower()
                    self.socketio.emit(category_event, {
                        'data': data,
                        'status': 200 if '_validation_errors' not in self.data_cache else 400
                    })

    def validate_battery_data(self, data):
        """Validate battery data against defined ranges"""
        if "Battery" not in data:
            return False, "Battery data not found", 400
        
        battery = data["Battery"]
        
        # Validate SOC
        soc = battery.get("SOC", 0)
        if not (self.valid_ranges["soc"][0] <= soc <= self.valid_ranges["soc"][1]):
            msg = f"SOC value {soc} outside valid range {self.valid_ranges['soc']}"
            logging.warning(msg)
            return False, msg, 400
        
        # Validate all cell voltages
        for i in range(1, 25):
            voltage_key = f"Voltage_{i}"
            voltage = battery.get(voltage_key, 0)
            if not (self.valid_ranges["cell_voltage"][0] <= voltage <= self.valid_ranges["cell_voltage"][1]):
                msg = f"{voltage_key} value {voltage} outside valid range {self.valid_ranges['cell_voltage']}"
                logging.warning(msg)
                return False, msg, 400
        
        return True, "Battery validation successful", 200

    def validate_tyre_data(self, data):
        """Validate tyre pressure data against defined ranges"""
        if "Tyre" not in data:
            return False, "Tyre data not found", 400
        
        tyre = data["Tyre"]
        tyre_positions = ["Right_Front", "Right_Back", "Left_Front", "Left_Back"]
        
        for position in tyre_positions:
            pressure = tyre.get(position, 0)
            if not (self.valid_ranges["tyre_pressure"][0] <= pressure <= self.valid_ranges["tyre_pressure"][1]):
                msg = f"Tyre pressure for {position} value {pressure} outside valid range {self.valid_ranges['tyre_pressure']}"
                logging.warning(msg)
                return False, msg, 400
        
        return True, "Tyre validation successful", 200

    def validate_ecu_data(self, data):
        """Validate ECU data"""
        if "LEVEL2_CU" not in data:
            return False, "ECU data not found", 400
        
        ecu_data = data["LEVEL2_CU"]
        for ecu_name, ecu_status in ecu_data.items():
            heartbeat = ecu_status.get("Heartbeat", 0)
            if heartbeat == 0:
                msg = f"ECU {ecu_name} heartbeat failure (value: {heartbeat})"
                logging.warning(msg)
                return False, msg, 400
            elif heartbeat not in [0, 1]:
                msg = f"Invalid heartbeat value for {ecu_name}: {heartbeat}"
                logging.warning(msg)
                return False, msg, 400
        return True, "ECU validation successful", 200

    def is_data_valid(self):
        """Check if current data is valid"""
        return '_validation_errors' not in self.data_cache if self.data_cache else False

    def update_data(self, new_data):
        """Update the data in the cache and file"""
        with self.lock:
            try:
                # Update the cache
                self.data_cache = new_data
                
                # Write to file
                with open(self.file_path, 'w') as file:
                    json.dump(new_data, file, indent=2)
                
                # Broadcast the updates
                self.broadcast_updates()
                
                logging.info("Data successfully updated")
                return True
            except Exception as e:
                logging.error(f"Error updating data: {str(e)}")
                return False