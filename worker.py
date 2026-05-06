from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, CommandHandler,
                           MessageHandler, filters, CallbackQueryHandler)
import database as db
from datetime import datetime

# States
LOGIN_USERNAME, LOGIN_PASSWORD, WRITE_REPORT, WRITE_REPORT_PHOTO = range(4)

MONTHS_UZ = {
    "01": "Yanvar", "02": "Fevral", "03": "Mart", "04": "Aprel",
    "05": "May", "06": "Iyun", "07": "Iyul", "08": "Avgust",
    "09": "Sentabr", "10": "Oktabr", "11": "Noyabr", "12": "Dekabr"
}

def get_month_name(month_str):
    parts = month_str.split("-")
    if len(parts) == 2:
        return f"{MONTHS_UZ.get(parts[1], parts[1])} {parts[0]}"
    return month_str

def worker_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Kunlik hisobot", callback_data="write_report")],
        [InlineKeyboardButton("🟢 Keldim", callback_data="att_in"),
         InlineKeyboardButton("🔴 Ketdim", callback_data="att_out")],
        [InlineKeyboardButton("⭐ Mening KPI'm", callback_data="my_kpi"),
         InlineKeyboardButton("🕐 Ish soatim", callback_data="my_hours")],
        [InlineKeyboardButton("📊 Mening statistikam", callback_data="my_stats")],
    ])

async def worker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    worker = db.get_worker_by_telegram(update.effective_user.id)
    if not worker:
        await update.message.reply_text(
            "🚫 Siz tizimga kirgansiz. Avval /login qiling."
        )
        return
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    await update.message.reply_text(
        f"👤 *{worker['full_name']}*\n"
        f"💼 {worker['position'] or 'Lavozim belgilanmagan'}\n"
        f"📅 {now}\n"
        f"─────────────────\n"
        f"Nimani qilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=worker_main_keyboard()
    )

async def worker_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    worker = db.get_worker_by_telegram(update.effective_user.id)
    if not worker:
        await query.edit_message_text("🚫 Avval /login qiling.")
        return
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    await query.edit_message_text(
        f"👤 *{worker['full_name']}*\n"
        f"💼 {worker['position'] or 'Lavozim belgilanmagan'}\n"
        f"📅 {now}\n"
        f"─────────────────\n"
        f"Nimani qilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=worker_main_keyboard()
    )

async def worker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    worker = db.get_worker_by_telegram(update.effective_user.id)
    if not worker:
        await query.edit_message_text("🚫 Avval /login qiling.")
        return

    if data == "att_in":
        db.mark_attendance(worker['id'], "in")
        now = datetime.now().strftime("%H:%M")
        await query.edit_message_text(
            f"🟢 *{worker['full_name']}* keldi!\n"
            f"⏰ Vaqt: *{now}*\n\n"
            f"Samarali ish kuni bo'lsin! 💪",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
        )

    elif data == "att_out":
        db.mark_attendance(worker['id'], "out")
        now = datetime.now().strftime("%H:%M")
        await query.edit_message_text(
            f"🔴 *{worker['full_name']}* ketdi!\n"
            f"⏰ Vaqt: *{now}*\n\n"
            f"Xayr! Yaxshi dam oling! 👋",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
        )

    elif data == "my_kpi":
        month = datetime.now().strftime("%Y-%m")
        month_name = get_month_name(month)
        kpis = db.get_worker_kpi(worker['id'], month)
        if not kpis:
            await query.edit_message_text(
                f"📭 *{month_name}* oyida sizga KPI belgilanmagan.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
            )
            return
        text = f"⭐ *{month_name.upper()} — KPI BALLARIM*\n{'─'*25}\n\n"
        total = 0
        for k in kpis:
            emoji = "🔴" if k['score'] <= 4 else ("🟡" if k['score'] <= 6 else "🟢")
            text += f"{emoji} Ball: *{k['score']}/10*\n"
            if k['comment']:
                text += f"   📝 {k['comment']}\n"
            text += "\n"
            total += k['score']
        if len(kpis) > 1:
            avg = total / len(kpis)
            text += f"📊 O'rtacha: *{avg:.1f}/10*"
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
        )

    elif data == "my_hours":
        month = datetime.now().strftime("%Y-%m")
        month_name = get_month_name(month)
        hours = db.get_worker_hours(worker['id'], month)
        if not hours:
            await query.edit_message_text(
                f"📭 *{month_name}* oyida ish soatingiz belgilanmagan.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
            )
            return
        await query.edit_message_text(
            f"🕐 *{month_name.upper()} — ISH SOATIM*\n{'─'*25}\n\n"
            f"⏰ Soat soni: *{hours['hours']}*\n"
            f"📝 Izoh: {hours['note'] or '—'}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
        )

    elif data == "my_stats":
        month = datetime.now().strftime("%Y-%m")
        month_name = get_month_name(month)
        reports = db.get_worker_reports(worker['id'], month)
        attendance = db.get_worker_attendance(worker['id'], month)
        kpis = db.get_worker_kpi(worker['id'], month)
        hours = db.get_worker_hours(worker['id'], month)

        in_count = sum(1 for a in attendance if a['att_type'] == 'in')
        out_count = sum(1 for a in attendance if a['att_type'] == 'out')
        avg_kpi = sum(k['score'] for k in kpis) / len(kpis) if kpis else 0

        text = (f"📊 *{month_name.upper()} — STATISTIKAM*\n{'─'*25}\n\n"
                f"📝 Hisobotlar: *{len(reports)} ta*\n"
                f"🟢 Keldi: *{in_count} marta*\n"
                f"🔴 Ketdi: *{out_count} marta*\n"
                f"⭐ KPI: *{avg_kpi:.1f}/10*\n"
                f"🕐 Ish soat: *{hours['hours'] if hours else '—'}*")

        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
        )

    elif data == "goto_menu":
        await worker_menu_callback(update, context)

# ==================== LOGIN ====================

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    worker = db.get_worker_by_telegram(update.effective_user.id)
    if worker:
        await update.message.reply_text(
            f"✅ Siz allaqachon kirgansiz: *{worker['full_name']}*\n\n"
            f"/menu — Menyuni ochish",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "🔑 *TIZIMGA KIRISH*\n\n"
        "1️⃣ Loginingizni kiriting:",
        parse_mode="Markdown"
    )
    return LOGIN_USERNAME

async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['login_username'] = update.message.text.strip()
    await update.message.reply_text(
        "2️⃣ Parolingizni kiriting:",
        parse_mode="Markdown"
    )
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    username = context.user_data.get('login_username', '')
    worker = db.get_worker_by_credentials(username, password)
    if worker:
        db.link_telegram(worker['id'], update.effective_user.id)
        await update.message.reply_text(
            f"✅ *Xush kelibsiz, {worker['full_name']}!*\n\n"
            f"💼 Lavozim: {worker['position'] or '—'}\n\n"
            f"/menu — Asosiy menyu",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Menyuni ochish", callback_data="goto_menu")]])
        )
    else:
        await update.message.reply_text(
            "❌ Login yoki parol noto'g'ri.\n\n"
            "Qayta urinish uchun /login\n"
            "Login/parol uchun adminга murojaat qiling."
        )
    context.user_data.clear()
    return ConversationHandler.END

# ==================== REPORT ====================

async def report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    worker = db.get_worker_by_telegram(update.effective_user.id)
    if not worker:
        await query.edit_message_text("🚫 Avval /login qiling.")
        return ConversationHandler.END
    context.user_data['report_worker_id'] = worker['id']
    today = datetime.now().strftime("%d.%m.%Y")
    await query.edit_message_text(
        f"📝 *KUNLIK HISOBOT — {today}*\n{'─'*25}\n\n"
        f"Bugun nima qildingiz?\n"
        f"• Qanday vazifalar bajarildi?\n"
        f"• Qanday natijalar?\n"
        f"• Muammolar bormi?\n\n"
        f"_Hisobotingizni yozing:_",
        parse_mode="Markdown"
    )
    return WRITE_REPORT

async def report_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) < 5:
        await update.message.reply_text("❌ Hisobot juda qisqa. Batafsil yozing:")
        return WRITE_REPORT
    context.user_data['report_text'] = text
    await update.message.reply_text(
        "📸 Rasm yubormoqchimisiz?\n\n"
        "_Rasm yuborish ixtiyoriy. O'tkazib yuborish uchun «O'tkazish» tugmasini bosing._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭ O'tkazish", callback_data="skip_photo")]])
    )
    return WRITE_REPORT_PHOTO

async def report_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file_id = photo.file_id
    worker_id = context.user_data['report_worker_id']
    report_text_data = context.user_data['report_text']

    db.add_report(worker_id, report_text_data, photo_file_id)
    today = datetime.now().strftime("%d.%m.%Y %H:%M")

    await update.message.reply_text(
        f"✅ *Hisobot saqlandi!*\n\n"
        f"📅 {today}\n"
        f"📸 Rasm qo'shildi",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
    )
    context.user_data.clear()
    return ConversationHandler.END

async def report_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    worker_id = context.user_data['report_worker_id']
    report_text_data = context.user_data['report_text']

    db.add_report(worker_id, report_text_data)
    today = datetime.now().strftime("%d.%m.%Y %H:%M")

    await query.edit_message_text(
        f"✅ *Hisobot saqlandi!*\n\n"
        f"📅 {today}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menyuga", callback_data="goto_menu")]])
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Bekor qilindi.\n\n/menu — Menyu"
    )
    return ConversationHandler.END

def get_login_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            LOGIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

def get_report_conv_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(report_start, pattern="^write_report$")],
        states={
            WRITE_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_text)],
            WRITE_REPORT_PHOTO: [
                MessageHandler(filters.PHOTO, report_photo),
                CallbackQueryHandler(report_skip_photo, pattern="^skip_photo$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
