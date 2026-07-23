# 🌐 Smart Network Monitoring System

A Flask-based web application that monitors network devices in real time, tracking their online/offline status through automated ping checks — with a live auto-refreshing dashboard, network auto-discovery, and full device management.

## 🚀 Features

- ✅ Real-time device status monitoring (online/offline) via ICMP ping
- ✅ Auto-refreshing dashboard (updates every 10 seconds, no page reload)
- ✅ Add/Delete devices directly from the web UI
- ✅ Network auto-discovery — scans the local subnet and finds all active devices
- ✅ SQLite database for persistent storage
- ✅ Clean, professional dashboard UI

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Networking | ICMP ping via Python subprocess, multithreaded subnet scanning |

## 📸 Screenshots

*(Add a screenshot of your dashboard here once you take one)*

## ⚙️ How It Works

1. Devices are added with a name and IP address (manually or via network scan)
2. A background check pings each device every 10 seconds
3. Status (online/offline) and last-checked timestamp are updated in the database
4. The dashboard reflects live status changes without manual refresh

## 🏃 Running Locally

```bash
# Clone the repository
git clone https://github.com/Bhagya242656/smart-Network-Monitoring-System.git
cd smart-Network-Monitoring-System

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python database/init_db.py

# Run the app
python app.py