from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from database.db import db


@dataclass
class Media:
    id: int
    trip_id: int
    file_path: str
    media_type: str

    @classmethod
    def get_by_id(cls, media_id: int):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trip_media WHERE id = ?", (media_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(*row)
        return None


@dataclass
class Trip:
    id: int
    created_at: str
    trip_date: str
    distance: Optional[float]
    duration: Optional[int]
    avg_speed: Optional[float]
    max_speed: Optional[float]
    min_elevation: Optional[float]
    max_elevation: Optional[float]
    elevation_gain: Optional[float]
    gpx_path: Optional[str]
    notes: Optional[str]

    @classmethod
    def create(cls, **kwargs) -> 'Trip':
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trips (trip_date, distance, duration, avg_speed, max_speed,
                             min_elevation, max_elevation, elevation_gain, gpx_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            kwargs.get('trip_date'),
            kwargs.get('distance'),
            kwargs.get('duration'),
            kwargs.get('avg_speed'),
            kwargs.get('max_speed'),
            kwargs.get('min_elevation'),
            kwargs.get('max_elevation'),
            kwargs.get('elevation_gain'),
            kwargs.get('gpx_path'),
            kwargs.get('notes')
        ))
        conn.commit()
        trip_id = cursor.lastrowid
        conn.close()
        return cls.get_by_id(trip_id)

    @classmethod
    def get_by_id(cls, trip_id: int) -> Optional['Trip']:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(*row)
        return None

    @classmethod
    def get_all(cls) -> List['Trip']:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips ORDER BY trip_date DESC, id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [cls(*row) for row in rows]

    @classmethod
    def get_paginated(cls, page: int, per_page: int) -> List['Trip']:
        offset = (page - 1) * per_page
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM trips 
            ORDER BY trip_date DESC, id DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        rows = cursor.fetchall()
        conn.close()
        return [cls(*row) for row in rows]

    @classmethod
    def count_all(cls) -> int:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trips")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @classmethod
    def get_last(cls) -> Optional['Trip']:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips ORDER BY trip_date DESC, id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(*row)
        return None

    def delete(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trips WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()

    def get_media(self) -> List[Media]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trip_media WHERE trip_id = ?", (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Media(*row) for row in rows]

    def add_media(self, file_path: str, media_type: str) -> Media:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trip_media (trip_id, file_path, media_type)
            VALUES (?, ?, ?)
        """, (self.id, file_path, media_type))
        conn.commit()
        media_id = cursor.lastrowid
        conn.close()
        return Media.get_by_id(media_id)

    def remove_media(self, media_id: int):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trip_media WHERE id = ?", (media_id,))
        conn.commit()
        conn.close()
