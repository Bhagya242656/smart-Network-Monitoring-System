# database/init_db.py

import sqlite3

# Connect to (or create) the database file
connection = sqlite3.connect('database/network_monitor.db')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create the 'devices' table if it doesn't already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        status TEXT DEFAULT 'unknown',
        last_checked TEXT
    )
''')

# Save changes to the database file
connection.commit()

# Close the connection
connection.close()

print("Database and 'devices' table created successfully!")