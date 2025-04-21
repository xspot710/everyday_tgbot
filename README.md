# Telegram Task Bot

A personal productivity-oriented Telegram bot designed to help track daily tasks, send reminders, and store task records in Firebase Firestore, with optional backup to SQLite.

---

## 📌 Features

- 📆 **Daily Task Reminders**  
  Automatically reminds users of their tasks for the day.

- ✅ **Task Completion Tracking**  
  Users can mark tasks as completed via chat commands or buttons.

- 🔄 **Data Backup**  
  Syncs all task data to Firebase Firestore, with support for exporting and deleting after backup.

- 💾 **Offline Backup**  
  Option to export all tasks to a local SQLite database for permanent record keeping.

- 🔒 **Inline Keyboards and Command Support**  
  User-friendly interaction using Telegram inline buttons and slash commands.

---

## ⚙️ Tech Stack

- **Language:** Python  
- **Bot Platform:** Telegram Bot API (via python-telegram-bot)  
- **Database:** Firebase Firestore + SQLite  
- **Task Format:** JSON-based templates  
- **Others:** pathlib, datetime, time modules

---

## 🚀 Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/xspot710/everyday_tgbot.git
cd everyday_tgbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your environment

Create a `.env` file with the following values:

```env
BOT_TOKEN=your_telegram_bot_token
```

### 4. Run the bot

```bash
python run.py
```

---

## 🛡 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## ✨ Future Improvements

- Data backup system
- Admin dashboard for reviewing task progress  
- Notification scheduler customization  
- Web-based interface for editing tasks  

---

## 👤 Author

Created by [xspot710](https://github.com/xspot710).  
