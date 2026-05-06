from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from admin import admin_callback, ADMIN_IDS
from worker import worker_callback
import database as db

ADMIN_CALLBACKS = [
    "list_workers", "today_reports", "monthly_report", "attendance",
    "add_worker", "del_worker", "set_kpi", "set_hours",
    "export_word", "export_excel", "export_pdf",
    "admin_back", "admin_stats"
]
WORKER_CALLBACKS = [
    "att_in", "att_out", "my_kpi", "write_report", "my_hours", "my_stats"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    worker = db.get_worker_by_telegram(user.id)
    if user.id in ADMIN_IDS:
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin panelga kirish", callback_data="goto_admin")]
        ]
        await update.message.reply_text(
            f"👋 Xush kelibsiz, *{user.first_name}*!\n\n"
            f"🔐 Siz *Admin* sifatida kirmoqdasiz.\n\n"
            f"/admin — Admin panel\n"
            f"/menu — Ishchi menyusi",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif worker:
        keyboard = [
            [InlineKeyboardButton("📋 Mening menyum", callback_data="goto_menu")]
        ]
        await update.message.reply_text(
            f"👋 Xush kelibsiz, *{worker['full_name']}*!\n\n"
            f"💼 Lavozim: {worker['position'] or '—'}\n\n"
            f"/menu — Asosiy menyu",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔑 Tizimga kirish", callback_data="goto_login")]
        ]
        await update.message.reply_text(
            "👋 *Korporativ boshqaruv tizimiga xush kelibsiz!*\n\n"
            "Bu tizim orqali:\n"
            "• 📝 Kunlik hisobot yozish\n"
            "• ⭐ KPI ballaringizni ko'rish\n"
            "• 🕐 Ish soatlaringizni kuzatish\n"
            "• 📊 Davomatni belgilash\n\n"
            "Davom etish uchun login va parolingiz kerak.\n"
            "Login/parol uchun adminga murojaat qiling.\n\n"
            "/login — Tizimga kirish",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def combined_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "goto_admin":
        from admin import admin_menu_callback
        await admin_menu_callback(update, context)
    elif data == "goto_menu":
        from worker import worker_menu_callback
        await worker_menu_callback(update, context)
    elif data == "goto_login":
        await query.answer()
        await query.edit_message_text(
            "🔑 Tizimga kirish uchun /login buyrug'ini yuboring."
        )
    elif any(data.startswith(cb) for cb in ADMIN_CALLBACKS) or data.startswith("del_") or data.startswith("kpi_") or data.startswith("hours_") or data.startswith("export_"):
        await admin_callback(update, context)
    elif any(data.startswith(cb) for cb in WORKER_CALLBACKS):
        await worker_callback(update, context)
    else:
        await query.answer("❌ Noma'lum buyruq", show_alert=False)
