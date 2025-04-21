from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskRecord:
    id: Optional[int]         # 主鍵
    date: str                 # yyyy-mm-dd
    category: str             # 任務分類
    task_name: str            # 任務名稱
    start_time: Optional[str] # HH:MM
    end_time: Optional[str]
    status: str               # 完成、略過、延後
    note: Optional[str] = ""  # 備註
    