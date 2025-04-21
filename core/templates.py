import pandas as pd
from pathlib import Path
from typing import List, Dict

TEMPLATE_PATH = Path("data/templates/daily_template.xlsx")

REQUIRED_COLUMNS = ["類別", "任務名稱", "建議時間", "預估時長（分鐘）", "備註"]

def load_template_from_excel(file_path: Path = TEMPLATE_PATH) -> List[Dict]:
    try:
        df = pd.read_excel(file_path)

        # 驗證欄位格式
        if not all(col in df.columns for col in REQUIRED_COLUMNS):
            raise ValueError(f"模板缺少必要欄位：{REQUIRED_COLUMNS}")

        return df.to_dict(orient="records")

    except Exception as e:
        print(f"[模板讀取失敗] {e}")
        return []