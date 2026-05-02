"""
utils.py
Handy utilities for manual testing:

  python utils.py add    — inserts 5 new random rows into input_data
  python utils.py view   — prints the predictions table
  python utils.py reset  — clears predictions (so predict.py will re-run)
"""

import sqlite3
import os
import random
import sys

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "sonar.db")
N_FEATURES = 60


def get_con():
    return sqlite3.connect(DB_PATH)


def add_rows(n=5):
    con = get_con()
    cur = con.cursor()
    cols = ", ".join(f"f{i}" for i in range(1, N_FEATURES + 1))
    ph   = ", ".join("?" * N_FEATURES)
    for _ in range(n):
        vals = [round(random.uniform(0.0, 1.0), 4) for _ in range(N_FEATURES)]
        cur.execute(f"INSERT INTO input_data ({cols}) VALUES ({ph})", vals)
    con.commit()
    con.close()
    print(f"Inserted {n} new row(s) into input_data.")


def view_predictions():
    con = get_con()
    cur = con.cursor()
    cur.execute("""
        SELECT p.id, p.prediction, p.prediction_timestamp
        FROM   predictions p
        ORDER  BY p.id
    """)
    rows = cur.fetchall()
    con.close()
    if not rows:
        print("No predictions yet.")
        return
    print(f"{'ID':>5}  {'Prediction':>12}  Timestamp")
    print("-" * 55)
    for row_id, pred, ts in rows:
        label = "Mine 💣" if pred == "M" else "Rock 🪨"
        print(f"{row_id:>5}  {label:>12}  {ts}")
    print(f"\nTotal: {len(rows)} prediction(s).")


def reset_predictions():
    con = get_con()
    cur = con.cursor()
    cur.execute("DELETE FROM predictions")
    con.commit()
    con.close()
    print("Predictions table cleared.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "view"
    if cmd == "add":
        add_rows(5)
    elif cmd == "reset":
        reset_predictions()
    else:
        view_predictions()
