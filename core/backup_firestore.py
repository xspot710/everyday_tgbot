import sqlite3
from pathlib import Path
from dataclasses import dataclass
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# ✅ TaskRecord 類別
@dataclass
class TaskRecord:
    id: int
    date: str
    category: str
    task_name: str
    start_time: str
    end_time: str
    status: str
    note: str

# ✅ Firestore 初始化
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    initialize_app(cred)
db = firestore.client()

# ✅ SQLite 初始化
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
    print("✅ SQLite 資料表已初始化")

def insert_task(record: TaskRecord):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO tasks (date, category, task_name, start_time, end_time, status, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (record.date, record.category, record.task_name, record.start_time, record.end_time, record.status, record.note))

# ✅ 備份流程
def backup_firestore_to_sqlite():
    init_db()
    tasks_ref = db.collection("tasks")
    docs = tasks_ref.stream()
    count = 0

    for doc in docs:
        data = doc.to_dict()
        try:
            record = TaskRecord(
                id=None,
                date=data.get("date"),
                category=data.get("category"),
                task_name=data.get("task_name"),
                start_time=data.get("start_time"),
                end_time=data.get("end_time"),
                status=data.get("status"),
                note=data.get("note", "")
            )
            insert_task(record)
            tasks_ref.document(doc.id).delete()
            count += 1
        except Exception as e:
            print(f"❌ 錯誤：{e}（文件 ID：{doc.id}）")

    print(f"✅ 成功備份 {count} 筆任務並從 Firestore 刪除")
    return count

# ✅ 執行
if __name__ == "__main__":
    backup_firestore_to_sqlite()