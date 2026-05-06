import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import database as db
from handlers.admin import get_admin_conv_handler, admin_menu, ADMIN_IDS
from handlers.worker import get_login_conv_handler, get_report_conv_handler, worker_menu
from handlers.common import start, combined_callback

TOKEN = "8654469405:AAEpEH7wKLz-0Ce4P0xfNP4RBohWO2PJ-VM"
MY_TELEGRAM_ID = 1131598666

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

async def main():
    db.init_db()
    ADMIN_IDS.append(MY_TELEGRAM_ID)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(get_login_conv_handler())
    app.add_handler(get_admin_conv_handler())
    app.add_handler(get_report_conv_handler())
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CommandHandler("menu", worker_menu))
    app.add_handler(CallbackQueryHandler(combined_callback))
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())