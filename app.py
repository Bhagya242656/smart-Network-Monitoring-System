# app.py

from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import sqlite3
import subprocess
import platform
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.secret_key = 'change-this-to-a-random-secret-key'  # needed for sessions

# Simple hardcoded login (fine for a learning project)
USERNAME = 'admin'
PASSWORD = 'admin123'

def get_all_devices():
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
    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO devices (name, ip_address, status) VALUES (?, ?, ?)',
        (name, ip_address, 'unknown')
    )
    connection.commit()
    connection.close()

def delete_device(device_id):
    connection = sqlite3.connect('database/network_monitor.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    connection.commit()
    connection.close()

def ping_device(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def update_device_status(device_id, ip_address):
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

def scan_network(base_ip):
    ips_to_scan = [f"{base_ip}.{i}" for i in range(1, 255)]
    found_devices = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_device, ips_to_scan)
    for ip, is_online in zip(ips_to_scan, results):
        if is_online:
            found_devices.append(ip)
    return found_devices

# ===== LOGIN ROUTES =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        entered_username = request.form.get('username')
        entered_password = request.form.get('password')

        if entered_username == USERNAME and entered_password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ===== MAIN ROUTES (protected) =====

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    devices = get_all_devices()
    return render_template('index.html', devices=devices)

@app.route('/api/devices')
def api_devices():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    devices = get_all_devices()
    return jsonify(devices)

@app.route('/api/devices/add', methods=['POST'])
def api_add_device():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    name = data.get('name')
    ip_address = data.get('ip_address')
    add_device(name, ip_address)
    return jsonify({'message': 'Device added successfully'}), 201

@app.route('/api/devices/delete/<int:device_id>', methods=['DELETE'])
def api_delete_device(device_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    delete_device(device_id)
    return jsonify({'message': 'Device deleted successfully'})

@app.route('/api/devices/check', methods=['POST'])
def api_check_devices():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    devices = get_all_devices()
    for device in devices:
        update_device_status(device['id'], device['ip_address'])
    return jsonify({'message': 'All devices checked successfully'})

@app.route('/api/network/scan', methods=['POST'])
def api_scan_network():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    base_ip = data.get('base_ip')
    found_ips = scan_network(base_ip)
    return jsonify({'found_devices': found_ips})

if __name__ == '__main__':
    app.run(debug=True)