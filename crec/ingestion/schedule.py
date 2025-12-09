import csv
import sqlite3
from pathlib import Path

from crec.config import config
from crec.ingestion.utils import sanitize_directory


def init_db(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        DROP TABLE IF EXISTS spring_schedule;
    """
    )

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS spring_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT NOT NULL,
        subject TEXT NOT NULL,
        catalog_num TEXT NOT NULL,
        section TEXT,
        course_name TEXT NOT NULL,
        start_time TEXT,
        end_time TEXT,
        scheduled_days TEXT,
        credits REAL NOT NULL
    );
    """,
    )

    conn.commit()
    conn.close()


def load_csv_into_db(db_path: str, csv_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        rows = [
            (
                row["Session"].strip(),
                row["Subject"].strip(),
                row["Catalog"].strip(),
                row["Section"].strip(),
                row["Descr"].strip(),
                row["Mtg Start"].strip(),
                row["Mtg End"].strip(),
                row["Schedule Days"].strip(),
                float(row["Max Units"]),
            )
            for row in reader
        ]

    cur.executemany(
        """
        INSERT INTO spring_schedule (
            session,
            subject,
            catalog_num,
            section,
            course_name,
            start_time,
            end_time,
            scheduled_days,
            credits
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
    conn.close()


def pipeline(data_dir: Path | str):
    paths = sanitize_directory(data_dir)
    csv_path = None
    for path in paths:
        if path.endswith(".csv"):
            csv_path = path
    if csv_path is None:
        msg = "Schedule csv file was not found in data directory."
        raise LookupError(msg)
    init_db(config.schedule_db)
    load_csv_into_db(config.schedule_db, csv_path)
