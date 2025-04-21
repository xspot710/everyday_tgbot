from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ForceReply
)
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from datetime import datetime
from core.templates import load_template_from_excel
import json
from pathlib import Path
from core.models import TaskRecord
import time
from core.firebase import save_task_to_firestore

PENDING_PATH = Path("data/pending_tasks")


def save_task_to_json(record: TaskRecord):
    PENDING_PATH.mkdir(parents=True, exist_ok=True)
    file_path = PENDING_PATH / f"{record.date}.json"

    data = []
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(record.__dict__)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 歡迎使用你的每日任務機器人\n\n"
        "我會協助你每天紀錄完成了哪些任務。\n"
        "請使用 /today 開始今天的任務！"
    )
    await update.message.reply_text(welcome_text)


# /today 指令
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = load_template_from_excel()
    if not tasks:
        await update.message.reply_text("⚠️ 無法載入任務模板")
        return

    context.user_data["task_messages"] = []

    for i, task in enumerate(tasks):
        text = f"📌 {task['任務名稱']}（{task['類別']}）\n建議時間：{task['建議時間']}\n預估時長：{task['預估時長（分鐘）']} 分鐘"
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 開始", callback_data=f"start_{i}")]
        ])
        msg = await update.message.reply_text(text, reply_markup=button)
        context.user_data["task_messages"].append(msg.message_id)


# 點擊 [開始]
async def handle_start_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_index = int(query.data.split("_")[1])
    tasks = load_template_from_excel()
    if task_index >= len(tasks):
        await query.edit_message_text("⚠️ 任務已失效或無效")
        return

    selected_task = tasks[task_index]

    if "task_messages" in context.user_data:
        for msg_id in context.user_data["task_messages"]:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
            except Exception as e:
                print(f"[刪除失敗] {e}")
        context.user_data.pop("task_messages")

    now = datetime.now()
    context.user_data["current_task"] = {
        "index": task_index,
        "task": selected_task,
        "message_id": None,  # 可填入該任務訊息ID
        "start_time": now.strftime("%H:%M"),
        "start_ts": int(time.mktime(now.timetuple()))
    }

    task_text = (
        f"🚧 你正在執行任務：{selected_task['任務名稱']}（{selected_task['類別']}）\n"
        f"建議時間：{selected_task['建議時間']}\n預估時長：{selected_task['預估時長（分鐘）']} 分鐘"
    )
    end_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹ 結束", callback_data="end_task")]
    ])
    sent_msg = await query.message.reply_text(task_text, reply_markup=end_button)
    context.user_data["current_task"]["message_id"] = sent_msg.message_id


# 點擊 [結束]
async def handle_end_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [KeyboardButton("✅ 完成"), KeyboardButton("❌ 取消")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.user_data["awaiting_reply"] = "task_status"

    await query.message.reply_text("請選擇任務狀態：", reply_markup=reply_markup)


# 回應任務狀態（完成／取消）
async def handle_status_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_reply") != "task_status":
        return

    status = update.message.text.strip()
    if status not in ["✅ 完成", "❌ 取消"]:
        return

    context.user_data["current_task"]["status"] = "完成" if "完成" in status else "取消"
    context.user_data["awaiting_reply"] = "task_note"
    context.user_data["current_task"]["status_msg_id"] = update.message.message_id  # 記下狀態選單那句

    await update.message.reply_text("請輸入任務備註（可留白）：", reply_markup=ForceReply())

# 回應備註
async def handle_note_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_reply") != "task_note":
        return

    if not update.message.reply_to_message:
        return

    task_data = context.user_data.get("current_task")
    if not task_data:
        return

    note = update.message.text.strip()
    now = datetime.now()

    start_ts = task_data["start_ts"]
    end_ts = int(time.mktime(now.timetuple()))
    duration_min = int((end_ts - start_ts) / 60)
    task_name = task_data["task"]["任務名稱"]

    record = TaskRecord(
        id=None,
        date=now.strftime("%Y-%m-%d"),
        category=task_data["task"]["類別"],
        task_name=task_name,
        start_time=task_data["start_time"],
        end_time=now.strftime("%H:%M"),
        status=task_data["status"],
        note=note,
    )

    # 加 timestamp
    record_dict = record.__dict__.copy()
    record_dict["start_ts"] = start_ts
    record_dict["end_ts"] = end_ts
    record_dict["duration_minutes"] = duration_min

    # file_path = PENDING_PATH / f"{record.date}.json"
    # data = []
    # if file_path.exists():
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         try:
    #             data = json.load(f)
    #         except json.JSONDecodeError:
    #             data = []
    # data.append(record_dict)
    # with open(file_path, "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)

    # 寫入 Firestore
    save_task_to_firestore(record_dict)

    # 🔥 刪除所有前段訊息
    chat_id = update.effective_chat.id
    message_ids_to_delete = [
        task_data.get("message_id"),                         # 任務進行訊息
        update.message.reply_to_message.message_id,          # ForceReply 問備註那句
        update.message.message_id,                           # 實際備註內容
        task_data.get("status_msg_id")                       # 狀態選單訊息
    ]
    for msg_id in message_ids_to_delete:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            print(f"[刪除訊息失敗] {e}")

    await update.message.reply_text(f"✅ 任務「{task_name}」已完成，總共花了 {duration_min} 分鐘！")

    context.user_data.pop("current_task", None)
    context.user_data.pop("awaiting_reply", None)


# 註冊所有指令與處理器
def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CallbackQueryHandler(handle_start_task, pattern=r"^start_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_end_task, pattern="^end_task$"))
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, handle_note_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_status_choice))

# def register_handlers(app):
#     async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
#         print(f"✅ 收到來自 {update.effective_user.username} 的 /start")
#         await update.message.reply_text("✅ Bot 正常回應囉！")

#     app.add_handler(CommandHandler("start", test))