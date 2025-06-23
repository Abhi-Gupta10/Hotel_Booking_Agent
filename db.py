import sqlite3

def init_db():
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        checkin TEXT,
        checkout TEXT,
        room_type TEXT,
        guests INTEGER
    )''')
    conn.commit()
    conn.close()

def save_booking(username, checkin, checkout, room_type, guests):
    conn = sqlite3.connect("hotel.db")
    c = conn.cursor()
    c.execute("INSERT INTO bookings (username, checkin, checkout, room_type, guests) VALUES (?, ?, ?, ?, ?)",
              (username, checkin, checkout, room_type, guests))
    conn.commit()
    conn.close()