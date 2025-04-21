import sqlite3
from pathlib import Path
from typing import List
from core.models import TaskRecord
from datetime import datetime

DB_PATH = Path("data/records.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                task_name TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                status TEXT NOT NULL,
                note TEXT
            )
        ''')
    print("[DB] Initialized.")

def insert_task(record: TaskRecord):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO tasks (date, category, task_name, start_time, end_time, status, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (record.date, record.category, record.task_name, record.start_time, record.end_time, record.status, record.note))

def get_tasks_by_date(date: str) -> List[TaskRecord]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute('''
            SELECT id, date, category, task_name, start_time, end_time, status, note
            FROM tasks
            WHERE date = ?
        ''', (date,))
        rows = cursor.fetchall()
        return [TaskRecord(*row) for row in rows]