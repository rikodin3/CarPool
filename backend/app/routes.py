from flask import Blueprint, jsonify, request
from app.simulator import simulator

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/status', methods=['GET'])
def status():
    return jsonify(simulator.get_full_status())

@routes_bp.route('/submit-request', methods=['POST'])
def submit_request():
    data = request.json
    res = simulator.submit_request(data.get('userId'), data.get('source'), data.get('destination'))
    return jsonify({**res, 'state': simulator.get_full_status()})
