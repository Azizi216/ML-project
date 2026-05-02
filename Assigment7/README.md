# Sonar Batch Prediction Pipeline

A production-style ML batch prediction system using **SQLite**, **scikit-learn**, and **APScheduler**.

The model is a `LogisticRegression` classifier trained on the **Sonar dataset** (60 acoustic features) that predicts whether an object is a **Mine (M)** or **Rock (R)**.

---

## Project Structure

```
batch_prediction_pipeline/
├── model.joblib      # Trained LogisticRegression model (60 features)
├── sonar.db          # SQLite database (auto-created by init_db.py)
├── init_db.py        # Creates tables + seeds 20 sample rows
├── predict.py        # Core batch prediction script
├── scheduler.py      # Runs predict.py on a schedule (every 5 min)
├── utils.py          # CLI helper: add rows / view results / reset
├── requirements.txt
└── README.md
```

---

## Database Schema

```sql
-- Input data table
CREATE TABLE input_data (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    f1  REAL NOT NULL,
    f2  REAL NOT NULL,
    ...
    f60 REAL NOT NULL
);

-- Predictions table
CREATE TABLE predictions (
    id                   INTEGER PRIMARY KEY,
    prediction           TEXT NOT NULL,      -- 'M' or 'R'
    prediction_timestamp TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES input_data(id)
);
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialise the database

```bash
python init_db.py
```

Creates `sonar.db` and seeds 20 random input rows.

### 3. Run a single prediction batch

```bash
python predict.py
```

Reads all unpredicted rows → generates predictions → writes to `predictions` table.

### 4. Start the scheduler (runs every 5 minutes)

```bash
python scheduler.py
```

Override the interval:

```bash
PREDICT_INTERVAL_MINUTES=10 python scheduler.py
```

### 5. Inspect results / add more data

```bash
python utils.py view    # show predictions table
python utils.py add     # insert 5 new random rows (will be predicted next run)
python utils.py reset   # clear predictions table
```

---

## Scheduling via System Cron (alternative to scheduler.py)

Run every 5 minutes using cron:

```bash
crontab -e
```

Add this line (adjust the path):

```cron
*/5 * * * * /usr/bin/python3 /path/to/batch_prediction_pipeline/predict.py >> /path/to/predict.log 2>&1
```

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│                  scheduler.py                   │
│         (APScheduler — every 5 min)             │
└────────────────────┬────────────────────────────┘
                     │ calls
                     ▼
┌─────────────────────────────────────────────────┐
│                   predict.py                    │
│                                                 │
│  1. Connect to sonar.db (SQLite)                │
│  2. SELECT unpredicted rows from input_data     │
│  3. Load model.joblib (LogisticRegression)      │
│  4. model.predict(features) → ['M','R', ...]   │
│  5. INSERT into predictions with timestamp      │
└─────────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
  input_data table        predictions table
  (60 feature cols)       (id, prediction,
                           prediction_timestamp)
```

---

## Model Details

| Property        | Value                   |
|-----------------|-------------------------|
| Type            | LogisticRegression      |
| Features        | 60 (sonar frequencies)  |
| Classes         | M (Mine), R (Rock)      |
| Penalty         | L2                      |
| Framework       | scikit-learn            |
