from telegram.ext import ApplicationBuilder
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import register_handlers

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 註冊所有指令與處理器
    register_handlers(app)

    print("🤖 Bot 已啟動，等待指令中...")
    app.run_polling()

if __name__ == "__main__":
    main()