import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# 初始化 Firebase
if not firebase_admin._apps:
    cred_path = Path("data/serviceAccountKey.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_task_to_firestore(task_dict: dict):
    try:
        db.collection("tasks").add(task_dict)
    except Exception as e:
        print(f"❌ 寫入 Firestore 失敗：{e}")