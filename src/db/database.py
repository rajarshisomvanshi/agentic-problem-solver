import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    files TEXT,  -- JSON list of file paths
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );
            """)

    def create_session(self, session_id: str, title: str):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title) VALUES (?, ?)",
                (session_id, title)
            )

    def add_message(self, session_id: str, role: str, content: str, files: List[str] = None):
        files_json = json.dumps(files or [])
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, files) VALUES (?, ?, ?, ?)",
                (session_id, role, content, files_json)
            )

    def get_sessions(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            )
            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                msg['files'] = json.loads(msg['files']) if msg['files'] else []
                messages.append(msg)
            return messages

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_session(self, session_id: str):
        with self._get_conn() as conn:
            # Foreign key constraints should cascade, but to be safe/explicit:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

# Global instance
db = Database()
