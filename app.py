# app.py

from flask import Flask, jsonify, request, render_template
import sqlite3
import subprocess
import platform
from datetime import datetime

app = Flask(__name__)

def get_all_devices():
    """Fetch all devices from the database."""
    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, ip_address, status, last_checked FROM devices')
    rows = cursor.fetchall()
    connection.close()

    devices = []
    for row in rows:
        devices.append({
            'id': row[0],
            'name': row[1],
            'ip_address': row[2],
            'status': row[3],
            'last_checked': row[4]
        })
    return devices

def add_device(name, ip_address):
    """Insert a new device into the database."""
    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO devices (name, ip_address, status) VALUES (?, ?, ?)',
        (name, ip_address, 'unknown')
    )
    connection.commit()
    connection.close()

def delete_device(device_id):
    """Remove a device from the database by its ID."""
    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    connection.commit()
    connection.close()

def ping_device(ip_address):
    """Ping a device and return True if online, False if offline."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def update_device_status(device_id, ip_address):
    """Ping a device and update its status + timestamp in the database."""
    is_online = ping_device(ip_address)
    status = 'online' if is_online else 'offline'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute(
        'UPDATE devices SET status = ?, last_checked = ? WHERE id = ?',
        (status, timestamp, device_id)
    )
    connection.commit()
    connection.close()

@app.route('/')
def home():
    devices = get_all_devices()
    return render_template('index.html', devices=devices)

@app.route('/api/devices')
def api_devices():
    devices = get_all_devices()
    return jsonify(devices)

@app.route('/api/devices/add', methods=['POST'])
def api_add_device():
    data = request.get_json()
    name = data.get('name')
    ip_address = data.get('ip_address')
    add_device(name, ip_address)
    return jsonify({'message': 'Device added successfully'}), 201

@app.route('/api/devices/delete/<int:device_id>', methods=['DELETE'])
def api_delete_device(device_id):
    delete_device(device_id)
    return jsonify({'message': 'Device deleted successfully'})

@app.route('/api/devices/check', methods=['POST'])
def api_check_devices():
    """Ping every device and update their status."""
    devices = get_all_devices()
    for device in devices:
        update_device_status(device['id'], device['ip_address'])
    return jsonify({'message': 'All devices checked successfully'})

if __name__ == '__main__':
    app.run(debug=True)