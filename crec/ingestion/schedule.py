import csv
import sqlite3

from crec.config import config


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


if __name__ == "__main__":
    csv_path = "/home/artemis/Developer/Course-Recommendation/data/class_schedule_session_3_spring_2026.csv"
    init_db(config.schedule_db)
    load_csv_into_db(config.schedule_db, csv_path)
