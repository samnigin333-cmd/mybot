import sqlite3
from datetime import datetime

DB_FILE = "data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        position TEXT DEFAULT '',
        telegram_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (date('now'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS daily_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER,
        report_text TEXT,
        photo_file_id TEXT DEFAULT '',
        date TEXT DEFAULT (date('now')),
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS kpi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER,
        score INTEGER,
        comment TEXT DEFAULT '',
        month TEXT,
        set_by INTEGER,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER,
        att_type TEXT,
        att_datetime TEXT DEFAULT (datetime('now')),
        note TEXT DEFAULT '',
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS work_hours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER,
        hours REAL,
        month TEXT,
        note TEXT DEFAULT '',
        set_by INTEGER,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(worker_id) REFERENCES workers(id)
    )''')

    conn.commit()
    conn.close()

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== WORKERS ====================

def add_worker(full_name, username, password, position=""):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO workers (full_name, username, password, position) VALUES (?, ?, ?, ?)",
            (full_name, username.lower().strip(), password.strip(), position)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_workers():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, full_name, username, position, telegram_id, is_active FROM workers WHERE is_active=1 ORDER BY full_name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_worker_by_credentials(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM workers WHERE username=? AND password=? AND is_active=1",
        (username.lower().strip(), password.strip())
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_worker_by_telegram(telegram_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM workers WHERE telegram_id=? AND is_active=1", (telegram_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_worker_by_id(worker_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM workers WHERE id=?", (worker_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def link_telegram(worker_id, telegram_id):
    conn = get_conn()
    conn.execute("UPDATE workers SET telegram_id=? WHERE id=?", (telegram_id, worker_id))
    conn.commit()
    conn.close()

def delete_worker(worker_id):
    conn = get_conn()
    conn.execute("UPDATE workers SET is_active=0, telegram_id=NULL WHERE id=?", (worker_id,))
    conn.commit()
    conn.close()

def update_worker_password(worker_id, new_password):
    conn = get_conn()
    conn.execute("UPDATE workers SET password=? WHERE id=?", (new_password, worker_id))
    conn.commit()
    conn.close()

# ==================== REPORTS ====================

def add_report(worker_id, text, photo_file_id=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO daily_reports (worker_id, report_text, photo_file_id) VALUES (?, ?, ?)",
        (worker_id, text, photo_file_id)
    )
    conn.commit()
    conn.close()

def get_reports_today():
    conn = get_conn()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT w.full_name, r.report_text, r.photo_file_id, r.created_at
        FROM daily_reports r
        JOIN workers w ON w.id = r.worker_id
        WHERE r.date = ?
        ORDER BY r.created_at
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_reports_by_month(month):
    conn = get_conn()
    rows = conn.execute("""
        SELECT w.full_name, r.report_text, r.photo_file_id, r.date, r.created_at
        FROM daily_reports r
        JOIN workers w ON w.id = r.worker_id
        WHERE r.date LIKE ?
        ORDER BY r.date, w.full_name
    """, (f"{month}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_worker_reports(worker_id, month):
    conn = get_conn()
    rows = conn.execute("""
        SELECT report_text, photo_file_id, date, created_at
        FROM daily_reports
        WHERE worker_id=? AND date LIKE ?
        ORDER BY date
    """, (worker_id, f"{month}%")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==================== KPI ====================

def add_kpi(worker_id, score, comment, month=None, set_by=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    conn.execute(
        "INSERT INTO kpi (worker_id, score, comment, month, set_by) VALUES (?, ?, ?, ?, ?)",
        (worker_id, score, comment, month, set_by)
    )
    conn.commit()
    conn.close()

def get_kpi_by_month(month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute("""
        SELECT w.full_name, k.score, k.comment, k.month, k.created_at, w.id as worker_id
        FROM kpi k
        JOIN workers w ON w.id = k.worker_id
        WHERE k.month = ?
        ORDER BY w.full_name
    """, (month,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_worker_kpi(worker_id, month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute(
        "SELECT score, comment, month, created_at FROM kpi WHERE worker_id=? AND month=? ORDER BY created_at",
        (worker_id, month)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==================== ATTENDANCE ====================

def mark_attendance(worker_id, att_type, note=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO attendance (worker_id, att_type, note) VALUES (?, ?, ?)",
        (worker_id, att_type, note)
    )
    conn.commit()
    conn.close()

def get_attendance_month(month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute("""
        SELECT w.full_name, a.att_type, a.att_datetime, a.note
        FROM attendance a
        JOIN workers w ON w.id = a.worker_id
        WHERE a.att_datetime LIKE ?
        ORDER BY a.att_datetime
    """, (f"{month}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_worker_attendance(worker_id, month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute(
        "SELECT att_type, att_datetime, note FROM attendance WHERE worker_id=? AND att_datetime LIKE ? ORDER BY att_datetime",
        (worker_id, f"{month}%")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==================== WORK HOURS ====================

def set_work_hours(worker_id, hours, month=None, note="", set_by=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    # Mavjud bo'lsa yangilash, bo'lmasa qo'shish
    existing = conn.execute(
        "SELECT id FROM work_hours WHERE worker_id=? AND month=?", (worker_id, month)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE work_hours SET hours=?, note=?, set_by=? WHERE worker_id=? AND month=?",
            (hours, note, set_by, worker_id, month)
        )
    else:
        conn.execute(
            "INSERT INTO work_hours (worker_id, hours, month, note, set_by) VALUES (?, ?, ?, ?, ?)",
            (worker_id, hours, month, note, set_by)
        )
    conn.commit()
    conn.close()

def get_work_hours_month(month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    rows = conn.execute("""
        SELECT w.full_name, wh.hours, wh.month, wh.note, w.id as worker_id
        FROM work_hours wh
        JOIN workers w ON w.id = wh.worker_id
        WHERE wh.month = ?
        ORDER BY w.full_name
    """, (month,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_worker_hours(worker_id, month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    row = conn.execute(
        "SELECT hours, month, note FROM work_hours WHERE worker_id=? AND month=?",
        (worker_id, month)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
