from flask import Flask, jsonify, request
from flask_cors import CORS
import database as db

app = Flask(__name__)
CORS(app)

@app.route('/workers', methods=['GET'])
def get_workers():
    workers = db.get_all_workers()
    return jsonify(workers)

@app.route('/attendance', methods=['GET'])
def get_attendance():
    month = request.args.get('month')
    data = db.get_attendance_month(month)
    return jsonify(data)

@app.route('/reports', methods=['GET'])
def get_reports():
    data = db.get_reports_today()
    return jsonify(data)

@app.route('/kpi', methods=['GET'])
def get_kpi():
    month = request.args.get('month')
    data = db.get_kpi_by_month(month)
    return jsonify(data)

@app.route('/login', methods=['POST'])
def login():
    body = request.json
    worker = db.get_worker_by_credentials(body['username'], body['password'])
    if worker:
        return jsonify({'success': True, 'worker': worker})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
