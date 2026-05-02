"""
predict.py
Batch prediction script:
  1. Connects to SQLite database
  2. Reads all input_data rows that don't yet have a prediction
  3. Loads the trained LogisticRegression model
  4. Generates predictions (M = Mine, R = Rock)
  5. Writes results to the predictions table with a timestamp
"""

import sqlite3
import logging
import os
from datetime import datetime, timezone

import joblib
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "sonar.db")
MODEL_PATH = os.path.join(BASE_DIR, "model (3).joblib")
N_FEATURES = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_model():
    """Load the trained sklearn model from disk."""
    log.info("Loading model from %s", MODEL_PATH)
    model = joblib.load(MODEL_PATH)
    log.info("Model loaded: %s", type(model).__name__)
    return model


def fetch_unpredicted(cur):
    """Return rows from input_data that have no entry in predictions yet."""
    feature_cols = ", ".join(f"i.f{k}" for k in range(1, N_FEATURES + 1))
    cur.execute(f"""
        SELECT i.id, {feature_cols}
        FROM   input_data i
        LEFT JOIN predictions p ON p.id = i.id
        WHERE  p.id IS NULL
    """)
    return cur.fetchall()


def run_batch():
    """Main batch prediction routine."""
    log.info("=" * 55)
    log.info("Batch prediction started")

    # ── Connect ──────────────────────────────────────────────
    if not os.path.exists(DB_PATH):
        log.error("Database not found: %s — run init_db.py first.", DB_PATH)
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # ── Fetch unpredicted rows ────────────────────────────────
    rows = fetch_unpredicted(cur)
    if not rows:
        log.info("No new rows to predict. Exiting.")
        con.close()
        return

    log.info("Found %d unpredicted row(s).", len(rows))

    # ── Load model ────────────────────────────────────────────
    model = load_model()

    # ── Build feature matrix ──────────────────────────────────
    ids      = [row[0] for row in rows]
    features = np.array([row[1:] for row in rows], dtype=float)

    # ── Predict ───────────────────────────────────────────────
    predictions = model.predict(features)          # array of 'M' or 'R'
    timestamp   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # ── Write results ─────────────────────────────────────────
    records = [(int(row_id), pred, timestamp) for row_id, pred in zip(ids, predictions)]
    cur.executemany(
        "INSERT OR IGNORE INTO predictions (id, prediction, prediction_timestamp) VALUES (?, ?, ?)",
        records,
    )
    con.commit()

    log.info("Stored %d prediction(s) at %s.", len(records), timestamp)

    # ── Summary ───────────────────────────────────────────────
    for row_id, pred in zip(ids, predictions):
        label = "Mine 💣" if pred == "M" else "Rock 🪨"
        log.info("  id=%d → %s (%s)", row_id, pred, label)

    con.close()
    log.info("Batch prediction finished.")
    log.info("=" * 55)


if __name__ == "__main__":
    run_batch()