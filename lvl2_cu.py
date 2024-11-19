from flask import Flask, Blueprint, jsonify
from flask_socketio import SocketIO
from message_manager import MessageManager
import logging

logger = logging.getLogger(__name__)

def start_lvl2_cu(port, message_manager: MessageManager):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode='gevent')

    # Define the status dictionary to keep track of the states
    lvl2_status = {
        "LEVEL2_CU": {
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
    }

    @app.route('/controlunitstatus/<ecu>/<attribute>/<value>', methods=['POST'])
    def set_ecu_status(ecu, attribute, value):
        try:
            if ecu in lvl2_status["LEVEL2_CU"]:
                if attribute in lvl2_status["LEVEL2_CU"][ecu]:
                    lvl2_status["LEVEL2_CU"][ecu][attribute] = value
                    # Update message manager
                    update_data = {
                        "type": "ECU_STATUS_UPDATE",
                        "data": {
                            "ecu": ecu,
                            "attribute": attribute,
                            "value": value
                        }
                    }
                    message_manager.update_data("Internal", update_data)
                    logger.info(f"Updated {ecu} {attribute} to {value}")
                    return jsonify({"status": "Success"}), 200
            return jsonify({"error": "Invalid ECU or attribute"}), 400
        except Exception as e:
            logger.error(f"Error in set_ecu_status: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/controlunitstatus/<ecu>/<attribute>', methods=['GET'])
    def get_ecu_status(ecu, attribute):
        try:
            if ecu in lvl2_status["LEVEL2_CU"]:
                if attribute in lvl2_status["LEVEL2_CU"][ecu]:
                    return jsonify({attribute: lvl2_status["LEVEL2_CU"][ecu][attribute]}), 200
            return jsonify({"error": "Invalid ECU or attribute"}), 400
        except Exception as e:
            logger.error(f"Error in get_ecu_status: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/status/lvl2controlunitstatus', methods=['GET'])
    def get_lvl2_control_unit_status():
        try:
            return jsonify({"LEVEL2_CU": lvl2_status["LEVEL2_CU"]}), 200
        except Exception as e:
            logger.error(f"Error in get_lvl2_control_unit_status: {e}")
            return jsonify({"error": str(e)}), 500

    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected to Level 2 Control Unit Service")

    logger.info(f"Level 2 Control Unit Service running on port {port}")
    socketio.run(app, host='0.0.0.0', port=port)