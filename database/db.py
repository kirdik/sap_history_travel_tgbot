import sqlite3
from datetime import datetime
from typing import List, Optional
import config


class Database:
    def __init__(self, db_path: str = "geobot.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trip_date DATE,
                distance REAL,
                duration INTEGER,
                avg_speed REAL,
                max_speed REAL,
                min_elevation REAL,
                max_elevation REAL,
                elevation_gain REAL,
                gpx_path TEXT,
                notes TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                media_type TEXT NOT NULL,
                FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()


db = Database()
