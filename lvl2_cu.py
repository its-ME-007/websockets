from flask import Flask, jsonify
from flask_socketio import SocketIO
from message_manager import MessageManager
import logging

logger = logging.getLogger(__name__)

def start_lvl2_service(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/lvl2cu')
    def handle_lvl2cu():
        data = message_manager.get_data()
        return {"LEVEL2_CU": data.get("LEVEL2_CU", {})}

    @app.route('/lvl2cu/<ecu>/<attribute>/<value>', methods=['POST'])
    def update_ecu_status(ecu, attribute, value):
        try:
            data = message_manager.get_data()
            if "LEVEL2_CU" not in data:
                data["LEVEL2_CU"] = {
                    "ECU1-VCU": {"Heartbeat": 0, "ActiveSoul": "MAIN/SHADOW"},
                    "ECUX-FCU": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU3-DoorECU": {"Heartbeat": 0, "ActiveSoul": "MAIN/SHADOW"},
                    "ECU4-RPi-OUT": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU5-RPi-IN": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU7-HVAC": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU8-USU": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU9-LCU": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU10-DashboardECU": {"Heartbeat": 0, "Status": "N/A"},
                    "ECU11-TableECU": {"Heartbeat": 0, "Status": "N/A"}
                }

            if ecu in data["LEVEL2_CU"]:
                if attribute in data["LEVEL2_CU"][ecu]:
                    data["LEVEL2_CU"][ecu][attribute] = value
                    message_manager.update_data(data)
                    logger.info(f"Updated {ecu} {attribute} to {value}")
                    return jsonify({"status": "Success"}), 200
            return jsonify({"error": "Invalid ECU or attribute"}), 400
        except Exception as e:
            logger.error(f"Error in update_ecu_status: {e}")
            return jsonify({"error": str(e)}), 500

    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected to Level 2 Control Unit Service")

    logger.info(f"Level 2 Control Unit Service running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)