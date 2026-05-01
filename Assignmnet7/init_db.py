import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS input_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature1 REAL,
    feature2 REAL,
    feature3 REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER,
    prediction REAL,
    prediction_timestamp TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized.")
