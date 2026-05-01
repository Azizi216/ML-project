import sqlite3
import pandas as pd
import joblib
from datetime import datetime

def run_batch_prediction():
    print(f"⏰ Job started at {datetime.now()}")

    conn = sqlite3.connect("database.db")
    df = pd.read_sql("SELECT * FROM input_data", conn)

    if df.empty:
        print("No data found.")
        return

    X = df.drop(columns=["id"])
    model = joblib.load("model.joblib")
    predictions = model.predict(X)

    cursor = conn.cursor()

    for i, pred in enumerate(predictions):
        cursor.execute("""
        INSERT INTO predictions (id, prediction, prediction_timestamp)
        VALUES (?, ?, ?)
        """, (
            int(df.iloc[i]["id"]),
            float(pred),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()

    print("✅ Predictions stored successfully.\n")

if __name__ == "__main__":
    run_batch_prediction()
