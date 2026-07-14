# test_ping.py

import subprocess
import platform

def ping_device(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Return code:", result.returncode)
    return result.returncode == 0

# Test it directly
is_online = ping_device('127.0.0.1')
print("Is online:", is_online)
