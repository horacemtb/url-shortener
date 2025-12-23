import sqlite3
import contextlib
from typing import Optional, Tuple
import os

class Database:
    def __init__(self):
        self.db_path = "/app/data/urls.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    short_id TEXT PRIMARY KEY,
                    full_url TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                )
            conn.commit()
    
    @contextlib.contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()