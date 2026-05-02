"""
init_db.py
Initializes the SQLite database with input_data and predictions tables,
and seeds input_data with sample Sonar dataset rows.
"""

import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sonar.db")
N_FEATURES = 60


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = get_connection()
    cur = con.cursor()

    # Create input_data table: id + 60 feature columns (f1..f60)
    feature_cols = ", ".join(f"f{i} REAL NOT NULL" for i in range(1, N_FEATURES + 1))
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS input_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {feature_cols}
        )
    """)

    # Create predictions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY,
            prediction  TEXT    NOT NULL,
            prediction_timestamp TEXT NOT NULL,
            FOREIGN KEY (id) REFERENCES input_data(id)
        )
    """)

    con.commit()

    # Seed with 20 random sample rows (if table is empty)
    cur.execute("SELECT COUNT(*) FROM input_data")
    if cur.fetchone()[0] == 0:
        print("Seeding input_data with 20 sample rows...")
        for _ in range(20):
            # Sonar features are floats in [0, 1]
            values = [round(random.uniform(0.0, 1.0), 4) for _ in range(N_FEATURES)]
            placeholders = ", ".join("?" * N_FEATURES)
            cur.execute(f"INSERT INTO input_data ({', '.join(f'f{i}' for i in range(1, N_FEATURES+1))}) VALUES ({placeholders})", values)
        con.commit()
        print("Seeding complete.")
    else:
        print("input_data already has rows — skipping seed.")

    con.close()
    print(f"Database ready at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
