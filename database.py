from datetime import date, datetime, timezone, timedelta
import html as html_lib
import os
import re
import sys
import time
import json
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
PSYCOPG_V3 = True
try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    try:
        import psycopg2 as psycopg
        import psycopg2.extras
        PSYCOPG_V3 = False
    except ImportError:
        raise ImportError("Modul 'psycopg' belum terpasang. Pastikan file requirements.txt berisi 'psycopg[binary]' dan 'psycopg'.")
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
HTML_FILE = os.path.join(PUBLIC_DIR, 'program.html')
TUTOR_HTML_FILE = os.path.join(PUBLIC_DIR, 'tutor.html')
ROOM_HTML_FILE = os.path.join(PUBLIC_DIR, 'ruang_belajar.html')
JADWAL_HTML_FILE = os.path.join(PUBLIC_DIR, 'jadwal.html')
PEMBAYARAN_HTML_FILE = os.path.join(PUBLIC_DIR, 'pembayaran.html')
TAGIHAN_HTML_FILE = os.path.join(PUBLIC_DIR, 'tagihan.html')
SISWA_HTML_FILE = os.path.join(PUBLIC_DIR, 'siswa.html')


# =============================================================================
# 1. KONEKSI KE DATABASE NEON POSTGRESQL
# =============================================================================

def create_new_connection():
    """Membuka dan mengembalikan koneksi baru ke Neon PostgreSQL"""
    try:
        # 1. Coba ambil dari file .env atau Environment Variable terlebih dahulu
        db_url = os.getenv("DATABASE_URL")

        # 2. Jika belum ada di .env, coba ambil dari Streamlit Secrets (Streamlit Cloud)
        if not db_url:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
                    db_url = st.secrets["DATABASE_URL"]
            except Exception:
                pass

        if db_url:
            return psycopg.connect(db_url)

        return psycopg.connect(
            dbname=os.getenv("POSTGRES_DB_NAME"),
            user=os.getenv("POSTGRES_USERNAME"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", 5432),
        )
    except psycopg.Error as e:
        raise Exception(f"Gagal menghubungkan ke database Neon: {e}")

get_connection = create_new_connection


# =============================================================================
# 2. FUNGSI PENGELOLAAN DATA PROGRAM (CRUD)
# =============================================================================

def get_programs():
    """Mengambil semua daftar program dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, level, sessions_per_month FROM programs ORDER BY id ASC;")
                return cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, level, sessions_per_month FROM programs ORDER BY id ASC;")
                return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_program(name, level, sessions=8):
    """Menambahkan program baru ke database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute("ALTER TABLE programs ALTER COLUMN level TYPE VARCHAR(60);")
            except Exception:
                pass
            cur.execute(
                "INSERT INTO programs (name, level, sessions_per_month) VALUES (%s, %s, %s) RETURNING id;",
                (name, level, sessions)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def delete_program(identifier):
    """Menghapus program berdasarkan ID atau Nama dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                cur.execute("DELETE FROM programs WHERE id = %s;", (int(identifier),))
            else:
                cur.execute("DELETE FROM programs WHERE name = %s;", (identifier,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


def update_program(identifier, name, level, sessions=8):
    """Memperbarui data program berdasarkan ID atau Nama di database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute("ALTER TABLE programs ALTER COLUMN level TYPE VARCHAR(60);")
            except Exception:
                pass
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                cur.execute(
                    "UPDATE programs SET name = %s, level = %s, sessions_per_month = %s WHERE id = %s;",
                    (name, level, int(sessions), int(identifier))
                )
            else:
                cur.execute(
                    "UPDATE programs SET level = %s, sessions_per_month = %s WHERE name = %s;",
                    (level, int(sessions), identifier)
                )
            updated = cur.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()


# =============================================================================
# 2B. FUNGSI PENGELOLAAN DATA TUTOR (CRUD)
# =============================================================================

def get_tutors():
    """Mengambil semua daftar tutor dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        # Pembersihan otomatis jika masih ada data legacy 'Matematika SD & SMP' di tabel tutors
        try:
            with conn.cursor() as cur_clean:
                cur_clean.execute(
                    """
                    UPDATE tutors
                    SET specialty = COALESCE(
                        (SELECT name FROM programs WHERE name ILIKE '%MATIK SD%' LIMIT 1),
                        (SELECT name FROM programs WHERE name ILIKE '%Matematika SD%' LIMIT 1),
                        (SELECT name FROM programs ORDER BY id ASC LIMIT 1),
                        'MATIK SD'
                    )
                    WHERE specialty ILIKE '%Matematika SD & SMP%';
                    """
                )
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass

        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC;")
                rows = cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC;")
                rows = [dict(r) for r in cur.fetchall()]

        # Pastikan tidak ada string legacy 'Matematika SD & SMP' yang lolos
        for t in rows:
            if "matematika sd & smp" in str(t.get('specialty') or "").strip().lower():
                t['specialty'] = 'MATIK SD'

        return rows
    finally:
        conn.close()


def add_tutor(name, specialty, phone, status='Aktif', email=None):
    """Menambahkan tutor baru ke database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tutors (name, specialty, phone, email, status) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (name, specialty, phone, email, status)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def delete_tutor(identifier):
    """Menghapus tutor berdasarkan ID atau Nama dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                cur.execute("DELETE FROM tutors WHERE id = %s;", (int(identifier),))
            else:
                cur.execute("DELETE FROM tutors WHERE name = %s;", (identifier,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


def update_tutor(tutor_id, name, specialty, phone, status='Aktif', email=None):
    """Memperbarui data tutor berdasarkan ID di database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            if email:
                cur.execute(
                    "UPDATE tutors SET name = %s, specialty = %s, phone = %s, status = %s, email = %s WHERE id = %s;",
                    (name, specialty, phone, status, email, int(tutor_id))
                )
            else:
                cur.execute(
                    "UPDATE tutors SET name = %s, specialty = %s, phone = %s, status = %s WHERE id = %s;",
                    (name, specialty, phone, status, int(tutor_id))
                )
            updated = cur.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()


# =============================================================================
# 2C. FUNGSI PENGELOLAAN DATA RUANG BELAJAR (CRUD)
# =============================================================================

def get_rooms():
    """Mengambil semua daftar ruang belajar dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, capacity, facilities FROM rooms ORDER BY id ASC;")
                return cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, capacity, facilities FROM rooms ORDER BY id ASC;")
                return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_room(name, capacity=5, facilities=None):
    """Menambahkan ruang belajar baru ke database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rooms (name, capacity, facilities) VALUES (%s, %s, %s) RETURNING id;",
                (name, int(capacity), facilities)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def delete_room(identifier):
    """Menghapus ruang belajar beserta jadwal terkait berdasarkan ID atau Nama dari Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                cur.execute("SELECT id FROM rooms WHERE id = %s;", (int(identifier),))
            else:
                cur.execute("SELECT id FROM rooms WHERE name = %s;", (identifier,))
            row = cur.fetchone()
            if not row:
                return False
            target_id = row[0]
            cur.execute(
                "DELETE FROM schedules WHERE study_group_id IN (SELECT id FROM study_groups WHERE room_id = %s);",
                (target_id,),
            )
            cur.execute("DELETE FROM rooms WHERE id = %s;", (target_id,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


HARI_ID = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}


def _fetch_schedules(room_id=None):
    """Helper terpadu mengambil jadwal kelas (semua ruang atau per room_id) dari Neon PostgreSQL."""
    conn = create_new_connection()
    where_clause = "WHERE sg.room_id = %s" if room_id is not None else ""
    query = f"""
        SELECT
            s.id AS schedule_id,
            s.day,
            s.start_time,
            s.end_time,
            sg.id AS study_group_id,
            sg.name AS group_name,
            sg.room_id,
            sg.tutor_id,
            sg.program_id,
            COALESCE(r.name, '-') AS room_name,
            COALESCE(t.name, '-') AS tutor_name,
            COALESCE(t.specialty, p.name, '-') AS subject_name,
            COALESCE(p.name, sg.name, '-') AS program_name
        FROM schedules s
        JOIN study_groups sg ON s.study_group_id = sg.id
        LEFT JOIN rooms r ON sg.room_id = r.id
        LEFT JOIN tutors t ON sg.tutor_id = t.id
        LEFT JOIN programs p ON sg.program_id = p.id
        {where_clause}
        ORDER BY
            CASE s.day
                WHEN 'Senin' THEN 1
                WHEN 'Selasa' THEN 2
                WHEN 'Rabu' THEN 3
                WHEN 'Kamis' THEN 4
                WHEN 'Jumat' THEN 5
                WHEN 'Sabtu' THEN 6
                WHEN 'Minggu' THEN 7
                ELSE 8
            END,
            s.start_time ASC,
            s.id ASC;
    """
    params = (int(room_id),) if room_id is not None else ()
    try:
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    now_wib = datetime.now(timezone(timedelta(hours=7)))
    hari_ini = HARI_ID.get(now_wib.weekday(), "")
    jam_sekarang = now_wib.strftime("%H:%M")

    for r in rows:
        day_str = str(r.get("day") or "").strip()
        start_str = str(r.get("start_time") or "").strip()
        end_str = str(r.get("end_time") or "").strip()
        r["is_ongoing"] = (
            day_str.lower() == hari_ini.lower()
            and bool(start_str)
            and bool(end_str)
            and start_str <= jam_sekarang <= end_str
        )
    return rows


def get_room_schedules(room_id):
    """Mengambil jadwal kelas yang berlangsung / terdaftar di suatu ruang belajar."""
    return _fetch_schedules(room_id=room_id)


def get_all_schedules():
    """Mengambil seluruh jadwal belajar lintas ruang dari Neon PostgreSQL."""
    return _fetch_schedules(room_id=None)


def _check_schedule_conflict(cur, day, start_time, end_time, room_id=None, tutor_id=None, exclude_schedule_id=None):
    """Memeriksa bentrok ruang maupun bentrok tutor pada hari yang sama dengan irisan jam."""
    if room_id:
        room_query = """
            SELECT COALESCE(r.name, 'Ruang'), s.start_time, s.end_time, COALESCE(p.name, sg.name)
            FROM schedules s
            JOIN study_groups sg ON s.study_group_id = sg.id
            LEFT JOIN rooms r ON sg.room_id = r.id
            LEFT JOIN programs p ON sg.program_id = p.id
            WHERE LOWER(s.day) = LOWER(%s)
              AND sg.room_id = %s
              AND s.start_time < %s
              AND %s < s.end_time
        """
        params = [day, int(room_id), end_time, start_time]
        if exclude_schedule_id:
            room_query += " AND s.id != %s"
            params.append(int(exclude_schedule_id))
        room_query += " LIMIT 1;"

        cur.execute(room_query, tuple(params))
        room_hit = cur.fetchone()
        if room_hit:
            raise ValueError(
                f"JADWAL BENTROK! {room_hit[0]} sudah digunakan kelas {room_hit[3]} "
                f"pada hari {day} pukul {room_hit[1]}–{room_hit[2]}."
            )

    if tutor_id:
        tutor_query = """
            SELECT COALESCE(t.name, 'Tutor'), s.start_time, s.end_time, COALESCE(r.name, 'Ruang')
            FROM schedules s
            JOIN study_groups sg ON s.study_group_id = sg.id
            LEFT JOIN tutors t ON sg.tutor_id = t.id
            LEFT JOIN rooms r ON sg.room_id = r.id
            WHERE LOWER(s.day) = LOWER(%s)
              AND sg.tutor_id = %s
              AND s.start_time < %s
              AND %s < s.end_time
        """
        params = [day, int(tutor_id), end_time, start_time]
        if exclude_schedule_id:
            tutor_query += " AND s.id != %s"
            params.append(int(exclude_schedule_id))
        tutor_query += " LIMIT 1;"

        cur.execute(tutor_query, tuple(params))
        tutor_hit = cur.fetchone()
        if tutor_hit:
            raise ValueError(
                f"TUTOR BENTROK! {tutor_hit[0]} sudah mengajar di {tutor_hit[3]} "
                f"pada hari {day} pukul {tutor_hit[1]}–{tutor_hit[2]}."
            )


def check_conflict(day, start_time, end_time, room_id=None, tutor_id=None, exclude_schedule_id=None):
    """Memeriksa apakah terdapat bentrok jadwal pada hari, jam, ruang, atau tutor tertentu di Neon PostgreSQL."""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            try:
                _check_schedule_conflict(cur, day, start_time, end_time, room_id=room_id, tutor_id=tutor_id, exclude_schedule_id=exclude_schedule_id)
                return {"conflict": False, "message": "Jadwal dan ruangan aman (tidak bentrok)."}
            except ValueError as e:
                return {"conflict": True, "message": str(e)}
    finally:
        conn.close()


def add_room_schedule(room_id, tutor_id, program_id, day, start_time, end_time, group_name=None):
    """Memeriksa bentrok lalu menambahkan jadwal kelas ke study_groups & schedules di Neon PostgreSQL."""
    start_clean = str(start_time or "").strip()
    end_clean = str(end_time or "").strip()
    if not start_clean or not end_clean:
        raise ValueError("Jam mulai dan jam selesai wajib diisi.")
    if start_clean >= end_clean:
        raise ValueError("Jam selesai harus lebih akhir dari jam mulai.")

    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            _check_schedule_conflict(cur, day, start_clean, end_clean, room_id=room_id, tutor_id=tutor_id)

            if not group_name:
                prog_label = "Kelas"
                if program_id:
                    cur.execute("SELECT name FROM programs WHERE id = %s;", (int(program_id),))
                    row = cur.fetchone()
                    if row and row[0]:
                        prog_label = row[0]
                group_name = prog_label

            cur.execute(
                """
                INSERT INTO study_groups (name, program_id, tutor_id, room_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    group_name,
                    int(program_id) if program_id else None,
                    int(tutor_id) if tutor_id else None,
                    int(room_id) if room_id else None,
                ),
            )
            sg_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO schedules (study_group_id, day, start_time, end_time)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (sg_id, day, start_clean, end_clean),
            )
            sched_id = cur.fetchone()[0]
        conn.commit()
        return sched_id
    finally:
        conn.close()


add_schedule = add_room_schedule


def delete_room_schedule(schedule_id):
    """Menghapus satu jadwal kelas berdasarkan schedule_id"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM schedules WHERE id = %s;", (int(schedule_id),))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


delete_schedule = delete_room_schedule


def update_room_schedule(schedule_id, room_id, tutor_id, program_id, day, start_time, end_time, group_name=None):
    """Memeriksa bentrok lalu memperbarui jadwal kelas di schedules & study_groups Neon PostgreSQL."""
    start_clean = str(start_time or "").strip()
    end_clean = str(end_time or "").strip()
    if not start_clean or not end_clean:
        raise ValueError("Jam mulai dan jam selesai wajib diisi.")
    if start_clean >= end_clean:
        raise ValueError("Jam selesai harus lebih akhir dari jam mulai.")

    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            _check_schedule_conflict(cur, day, start_clean, end_clean, room_id=room_id, tutor_id=tutor_id, exclude_schedule_id=int(schedule_id))

            cur.execute("SELECT study_group_id FROM schedules WHERE id = %s;", (int(schedule_id),))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Jadwal dengan ID {schedule_id} tidak ditemukan.")
            sg_id = row[0]

            if not group_name:
                prog_label = "Kelas"
                if program_id:
                    cur.execute("SELECT name FROM programs WHERE id = %s;", (int(program_id),))
                    prow = cur.fetchone()
                    if prow and prow[0]:
                        prog_label = prow[0]
                group_name = prog_label

            if sg_id:
                cur.execute(
                    """
                    UPDATE study_groups
                    SET name = %s, program_id = %s, tutor_id = %s, room_id = %s
                    WHERE id = %s;
                    """,
                    (
                        group_name,
                        int(program_id) if program_id else None,
                        int(tutor_id) if tutor_id else None,
                        int(room_id) if room_id else None,
                        sg_id,
                    ),
                )

            cur.execute(
                """
                UPDATE schedules
                SET day = %s, start_time = %s, end_time = %s
                WHERE id = %s;
                """,
                (day, start_clean, end_clean, int(schedule_id)),
            )
            updated = cur.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()


update_schedule = update_room_schedule


# =============================================================================
# 2D. FUNGSI PENGELOLAAN DATA TAGIHAN & PEMBAYARAN (CRUD)
# =============================================================================

def format_rupiah(nominal):
    """Memformat angka menjadi string Rp xxx.xxx"""
    val = int(round(float(nominal or 0)))
    return f"Rp {val:,}".replace(",", ".")


def _ensure_billing_tables_and_seed(conn):
    """Memastikan tabel bills & payments ada dan mengisi data awal jika masih kosong."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id SERIAL PRIMARY KEY,
                invoice_no VARCHAR(50) UNIQUE NOT NULL,
                student_id INTEGER,
                student_name VARCHAR(150),
                program_name VARCHAR(100),
                amount NUMERIC(12, 2) NOT NULL,
                due_date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'Belum Lunas',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("ALTER TABLE bills ADD COLUMN IF NOT EXISTS student_name VARCHAR(150);")
        cur.execute("ALTER TABLE bills ADD COLUMN IF NOT EXISTS program_name VARCHAR(100);")
        cur.execute("ALTER TABLE bills ADD COLUMN IF NOT EXISTS period VARCHAR(50) DEFAULT 'Oktober 2026';")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                receipt_no VARCHAR(50) UNIQUE NOT NULL,
                bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
                amount NUMERIC(12, 2) NOT NULL,
                payment_date DATE NOT NULL,
                payment_method VARCHAR(50) DEFAULT 'Transfer Bank',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("SELECT COUNT(*) FROM bills;")
        bill_count = cur.fetchone()[0]
        if bill_count == 0:
            today_wib = datetime.now(timezone(timedelta(hours=7))).date()
            future_due = today_wib + timedelta(days=14)
            past_due = today_wib - timedelta(days=14)

            seed_bills = [
                ("TGH-202610-001", "Alya Putri", "Calistung", 200000, past_due, "Lunas", 200000, "KWT-202610-001", "Oktober 2026"),
                ("TGH-202610-002", "Bagas Pratama", "Matematika SMP", 300000, past_due, "Belum Lunas", 150000, "KWT-202610-002", "Oktober 2026"),
                ("TGH-202610-003", "Citra Maharani", "Persiapan UTBK", 450000, future_due, "Belum Lunas", 0, None, "Oktober 2026"),
                ("TGH-202610-004", "Dimas Aditya", "Matematika SMP", 300000, past_due, "Belum Lunas", 0, None, "Oktober 2026"),
                ("TGH-202610-005", "Eka Lestari", "Matematika SD", 250000, future_due, "Belum Lunas", 100000, "KWT-202610-003", "Oktober 2026"),
            ]
            for inv, sname, pname, amt, ddate, st, paid_amt, rcpt, prd in seed_bills:
                cur.execute(
                    """
                    INSERT INTO bills (invoice_no, student_name, program_name, amount, due_date, status, period)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (inv, sname, pname, amt, ddate, st, prd),
                )
                b_id = cur.fetchone()[0]
                if paid_amt > 0 and rcpt:
                    cur.execute(
                        """
                        INSERT INTO payments (receipt_no, bill_id, amount, payment_date, payment_method, notes)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (rcpt, b_id, paid_amt, today_wib, "Transfer Bank", "Pembayaran awal"),
                    )
    conn.commit()


def get_billing_summary():
    """Mengambil daftar tagihan beserta total dibayar, sisa, status, dan ringkasan angka."""
    conn = create_new_connection()
    try:
        _ensure_billing_tables_and_seed(conn)
        query = """
            SELECT
                b.id AS bill_id,
                b.invoice_no,
                COALESCE(st.name, b.student_name, 'Siswa') AS student_name,
                COALESCE(pr.name, b.program_name, 'Bimbel') AS program_name,
                COALESCE(b.period, 'Oktober 2026') AS period,
                b.amount AS total_amount,
                b.due_date,
                COALESCE(SUM(p.amount), 0) AS paid_amount,
                COUNT(p.id) AS payment_count
            FROM bills b
            LEFT JOIN students st ON b.student_id = st.id
            LEFT JOIN programs pr ON st.program_id = pr.id
            LEFT JOIN payments p ON b.id = p.bill_id
            GROUP BY b.id, b.invoice_no, st.name, b.student_name, pr.name, b.program_name, b.period, b.amount, b.due_date
            ORDER BY b.id ASC;
        """
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query)
                rows = cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute(query)
                rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    today_wib = datetime.now(timezone(timedelta(hours=7))).date()
    bills = []
    stats = {"lunas": 0, "belum_lunas": 0, "menunggak": 0, "sudah_bayar": 0, "belum_bayar": 0}

    for r in rows:
        total_amt = int(round(float(r.get("total_amount") or 0)))
        paid_amt = int(round(float(r.get("paid_amount") or 0)))
        remaining = max(0, total_amt - paid_amt)

        due_raw = r.get("due_date")
        if isinstance(due_raw, datetime):
            due_dt = due_raw.date()
        elif isinstance(due_raw, date):
            due_dt = due_raw
        else:
            try:
                due_dt = datetime.strptime(str(due_raw)[:10], "%Y-%m-%d").date()
            except Exception:
                due_dt = today_wib

        if remaining <= 0:
            status_label = "Lunas"
            badge_class = "badge-status badge-status-lunas"
            is_lunas = True
            stats["lunas"] += 1
            stats["sudah_bayar"] += 1
        elif today_wib > due_dt:
            status_label = "Menunggak"
            badge_class = "badge-status badge-status-menunggak"
            is_lunas = False
            stats["menunggak"] += 1
            stats["belum_bayar"] += 1
        else:
            status_label = "Belum lunas"
            badge_class = "badge-status badge-status-belum"
            is_lunas = False
            stats["belum_lunas"] += 1
            stats["belum_bayar"] += 1

        bills.append({
            "bill_id": int(r["bill_id"]),
            "invoice_no": str(r["invoice_no"]),
            "student_name": str(r["student_name"]),
            "program_name": str(r["program_name"]),
            "period": str(r.get("period") or "Oktober 2026"),
            "total_amount": total_amt,
            "paid_amount": paid_amt,
            "remaining_amount": remaining,
            "due_date": due_dt.isoformat(),
            "due_date_str": due_dt.strftime("%d/%m/%Y"),
            "status": status_label,
            "badge_class": badge_class,
            "is_lunas": is_lunas,
            "payment_count": int(r.get("payment_count") or 0),
        })

    return {"bills": bills, "stats": stats}


def add_bill(student_name, program_name, amount, due_date=None):
    """Menambahkan tagihan siswa baru ke Neon PostgreSQL."""
    amt = int(round(float(amount or 0)))
    if not student_name or amt <= 0:
        raise ValueError("Nama siswa dan nominal tagihan valid wajib diisi.")

    today_wib = datetime.now(timezone(timedelta(hours=7))).date()
    if not due_date:
        due_date = today_wib + timedelta(days=14)

    conn = create_new_connection()
    try:
        _ensure_billing_tables_and_seed(conn)
        with conn.cursor() as cur:
            inv_no = f"TGH-{datetime.now().strftime('%Y%m%d')}-{int(time.time() * 1000) % 10000:04d}"
            cur.execute(
                """
                INSERT INTO bills (invoice_no, student_name, program_name, amount, due_date, status)
                VALUES (%s, %s, %s, %s, %s, 'Belum Lunas')
                RETURNING id;
                """,
                (inv_no, student_name.strip(), (program_name or "Bimbel").strip(), amt, due_date),
            )
            bill_id = cur.fetchone()[0]
        conn.commit()
        return bill_id
    finally:
        conn.close()


def add_payment(bill_id, amount, payment_method="Transfer Bank", notes=None):
    """Mencatat pembayaran untuk tagihan siswa ke tabel payments di Neon PostgreSQL."""
    amt = int(round(float(amount or 0)))
    if amt <= 0:
        raise ValueError("Nominal pembayaran harus lebih besar dari 0.")

    today_wib = datetime.now(timezone(timedelta(hours=7))).date()
    conn = create_new_connection()
    try:
        _ensure_billing_tables_and_seed(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT amount FROM bills WHERE id = %s;", (int(bill_id),))
            row = cur.fetchone()
            if not row:
                raise ValueError("Data tagihan tidak ditemukan.")
            bill_total = float(row[0] or 0)

            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE bill_id = %s;", (int(bill_id),))
            already_paid = float(cur.fetchone()[0] or 0)

            rcpt_no = f"KWT-{datetime.now().strftime('%Y%m%d')}-{int(time.time() * 1000) % 10000:04d}"
            cur.execute(
                """
                INSERT INTO payments (receipt_no, bill_id, amount, payment_date, payment_method, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (rcpt_no, int(bill_id), amt, today_wib, payment_method, notes or "Pembayaran tagihan"),
            )
            pay_id = cur.fetchone()[0]

            new_status = "Lunas" if (already_paid + amt) >= bill_total else "Belum Lunas"
            cur.execute("UPDATE bills SET status = %s WHERE id = %s;", (new_status, int(bill_id)))
        conn.commit()
        return pay_id
    finally:
        conn.close()


def delete_bill_payment(bill_id):
    """
    Jika tagihan punya riwayat pembayaran, menghapus seluruh pembayaran pada tagihan tsb (reset ke belum bayar).
    Jika belum ada pembayaran sama sekali, menghapus tagihan tsb.
    """
    conn = create_new_connection()
    try:
        _ensure_billing_tables_and_seed(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM payments WHERE bill_id = %s;", (int(bill_id),))
            pay_count = cur.fetchone()[0]
            if pay_count > 0:
                cur.execute("DELETE FROM payments WHERE bill_id = %s;", (int(bill_id),))
                cur.execute("UPDATE bills SET status = 'Belum Lunas' WHERE id = %s;", (int(bill_id),))
                action_type = "reset_payment"
            else:
                cur.execute("DELETE FROM bills WHERE id = %s;", (int(bill_id),))
                action_type = "deleted_bill"
        conn.commit()
        return action_type
    finally:
        conn.close()


def get_bills_by_period(period="Oktober 2026"):
    """Mengambil daftar tagihan berdasarkan periode tertentu dari Neon PostgreSQL."""
    summary = get_billing_summary()
    all_bills = summary["bills"]
    filtered = [
        b for b in all_bills
        if str(b.get("period") or "Oktober 2026").strip().lower() == str(period).strip().lower()
    ]
    return filtered


def publish_bills_for_period(period="Oktober 2026"):
    """
    Menerbitkan tagihan untuk seluruh siswa aktif pada periode tertentu di Neon PostgreSQL.
    Jika sudah terbit di periode tsb, mengembalikan daftar tagihannya.
    """
    existing = get_bills_by_period(period)
    if existing:
        return existing

    conn = create_new_connection()
    try:
        _ensure_billing_tables_and_seed(conn)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.name, COALESCE(p.name, 'Bimbel') AS program_name
                FROM students s
                LEFT JOIN programs p ON s.program_id = p.id
                WHERE LOWER(s.status) = 'aktif'
                ORDER BY s.id ASC;
            """)
            students = cur.fetchall()

            if not students:
                students_data = [
                    (None, "Alya Putri", "Calistung", 200000),
                    (None, "Bagas Pratama", "Matematika SMP", 300000),
                    (None, "Citra Maharani", "Persiapan UTBK", 450000),
                    (None, "Dimas Aditya", "Matematika SMP", 300000),
                    (None, "Eka Lestari", "Matematika SD", 250000),
                ]
            else:
                tarif_map = {
                    "calistung": 200000,
                    "matematika sd": 250000,
                    "matematika smp": 300000,
                    "ipa terpadu": 300000,
                    "persiapan utbk": 450000,
                }
                students_data = []
                for s in students:
                    s_id, s_name, p_name = s[0], s[1], s[2] or "Bimbel"
                    tarif = tarif_map.get(p_name.strip().lower(), 250000)
                    students_data.append((s_id, s_name, p_name, tarif))

            m = re.search(r'(\w+)\s+(\d{4})', str(period))
            if m:
                bln_name = m.group(1).lower()
                year = m.group(2)
                bln_map = {
                    'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
                    'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
                    'september': '09', 'oktober': '10', 'november': '11', 'desember': '12',
                }
                ym = f"{year}{bln_map.get(bln_name, '10')}"
            else:
                ym = datetime.now().strftime('%Y%m')

            today_wib = datetime.now(timezone(timedelta(hours=7))).date()
            due_dt = today_wib + timedelta(days=14)

            for idx, (s_id, s_name, p_name, amt) in enumerate(students_data, start=1):
                inv_no = f"TGH-{ym}-{idx:03d}"
                cur.execute(
                    """
                    INSERT INTO bills (invoice_no, student_id, student_name, program_name, amount, due_date, status, period)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Belum Lunas', %s)
                    ON CONFLICT (invoice_no) DO NOTHING;
                    """,
                    (inv_no, s_id, s_name, p_name, amt, due_dt, period),
                )
        conn.commit()
        return get_bills_by_period(period)
    finally:
        conn.close()


# =============================================================================
# 2E. FUNGSI PENGELOLAAN DATA SISWA DAN WALI (CRUD)
# =============================================================================

def _ensure_student_tables_and_seed(conn):
    """Memastikan struktur tabel students lengkap dan data awal siswa tersedia di Neon PostgreSQL"""
    try:
        with conn.cursor() as cur:
            # 1. Pastikan kolom level ada
            cur.execute("ALTER TABLE students ADD COLUMN IF NOT EXISTS level VARCHAR(20) DEFAULT 'SD';")
            try:
                cur.execute("ALTER TABLE students ALTER COLUMN gender DROP NOT NULL;")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE students ALTER COLUMN guardian_name DROP NOT NULL;")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE students ALTER COLUMN phone DROP NOT NULL;")
            except Exception:
                pass

            # 2. Cek apakah tabel siswa masih kosong
            cur.execute("SELECT COUNT(*) FROM students;")
            count = cur.fetchone()[0]
            if count == 0:
                demo_students = [
                    ('OPT-2026-001', 'Alya Putri', 'P', 'SD', 'Ibu Ratna', '0812-3456-7801', 'Aktif'),
                    ('OPT-2026-002', 'Bagas Pratama', 'L', 'SMP', 'Bapak Hendra', '0813-2211-4402', 'Aktif'),
                    ('OPT-2026-003', 'Citra Maharani', 'P', 'SMA', 'Ibu Sari', '0857-9012-3305', 'Aktif'),
                    ('OPT-2026-004', 'Dimas Aditya', 'L', 'SMP', 'Bapak Joko', '0821-7788-9906', 'Aktif'),
                    ('OPT-2026-005', 'Eka Lestari', 'P', 'SD', 'Ibu Wulan', '0878-1234-5507', 'Aktif'),
                ]
                cur.executemany(
                    """
                    INSERT INTO students (nis, name, gender, level, guardian_name, phone, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nis) DO NOTHING;
                    """,
                    demo_students,
                )
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass


def get_students():
    """Mengambil semua daftar siswa dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        _ensure_student_tables_and_seed(conn)
        query = """
            SELECT 
                s.id, 
                s.nis, 
                s.name, 
                COALESCE(s.gender, 'L') AS gender, 
                COALESCE(s.level, 'SD') AS level, 
                COALESCE(s.guardian_name, '-') AS guardian_name, 
                COALESCE(s.phone, '-') AS phone, 
                s.program_id, 
                pr.name AS program_name,
                COALESCE(s.status, 'Aktif') AS status,
                s.created_at
            FROM students s
            LEFT JOIN programs pr ON s.program_id = pr.id
            ORDER BY s.id ASC;
        """
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query)
                return cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute(query)
                return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_student(name, level='SD', guardian_name='-', phone='-', gender='L', nis=None, status='Aktif', program_id=None):
    """Menambahkan data siswa baru ke database Neon PostgreSQL"""
    if not name or not str(name).strip():
        raise ValueError("Nama siswa wajib diisi.")

    clean_name = str(name).strip()
    clean_level = (level or 'SD').strip().upper()
    clean_guardian = (guardian_name or '-').strip()
    clean_phone = (phone or '-').strip()
    clean_gender = (gender or 'L').strip().upper()
    clean_status = (status or 'Aktif').strip()

    conn = create_new_connection()
    try:
        _ensure_student_tables_and_seed(conn)
        with conn.cursor() as cur:
            if not nis or not str(nis).strip():
                cur.execute("SELECT COALESCE(MAX(id), 0) FROM students;")
                max_id = cur.fetchone()[0] or 0
                auto_nis = f"OPT-2026-{(int(max_id) + 1):03d}"
                cur.execute("SELECT id FROM students WHERE nis = %s;", (auto_nis,))
                if cur.fetchone():
                    auto_nis = f"OPT-2026-{int(time.time()) % 10000:04d}"
                final_nis = auto_nis
            else:
                final_nis = str(nis).strip()

            cur.execute(
                """
                INSERT INTO students (nis, name, gender, level, guardian_name, phone, program_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (final_nis, clean_name, clean_gender, clean_level, clean_guardian, clean_phone, program_id, clean_status)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_student(student_id, name=None, level=None, guardian_name=None, phone=None, gender=None, status=None, program_id=None, nis=None):
    """Memperbarui data siswa di database Neon PostgreSQL"""
    if not student_id:
        raise ValueError("ID siswa wajib diisi.")

    conn = create_new_connection()
    try:
        _ensure_student_tables_and_seed(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id, nis, name, gender, level, guardian_name, phone, status, program_id FROM students WHERE id = %s;", (int(student_id),))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Siswa dengan ID {student_id} tidak ditemukan.")

            cur_nis, cur_name, cur_gender, cur_lvl, cur_guardian, cur_phone, cur_status, cur_prog = (
                row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
            )

            new_name = str(name).strip() if name and str(name).strip() else cur_name
            new_level = (level or cur_lvl or 'SD').strip().upper()
            new_guardian = str(guardian_name).strip() if guardian_name is not None and str(guardian_name).strip() else cur_guardian
            new_phone = str(phone).strip() if phone is not None and str(phone).strip() else cur_phone
            new_gender = (gender or cur_gender or 'L').strip().upper()
            new_status = (status or cur_status or 'Aktif').strip()
            new_nis = (nis or cur_nis).strip()
            new_prog = program_id if program_id is not None else cur_prog

            cur.execute(
                """
                UPDATE students 
                SET nis = %s, name = %s, gender = %s, level = %s, guardian_name = %s, phone = %s, status = %s, program_id = %s
                WHERE id = %s;
                """,
                (new_nis, new_name, new_gender, new_level, new_guardian, new_phone, new_status, new_prog, int(student_id))
            )
            updated = cur.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()


def delete_student(identifier):
    """Menghapus siswa berdasarkan ID atau Nama atau NIS dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            s_id = None
            if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
                s_id = int(identifier)
            else:
                cur.execute("SELECT id FROM students WHERE nis = %s OR name = %s LIMIT 1;", (identifier, identifier))
                res = cur.fetchone()
                if res:
                    s_id = res[0]

            if s_id is not None:
                try:
                    cur.execute("UPDATE bills SET student_id = NULL WHERE student_id = %s;", (s_id,))
                except Exception:
                    pass
                try:
                    cur.execute("DELETE FROM attendances WHERE student_id = %s;", (s_id,))
                except Exception:
                    pass
                cur.execute("DELETE FROM students WHERE id = %s;", (s_id,))
                deleted = cur.rowcount > 0
            else:
                deleted = False
        conn.commit()
        return deleted
    finally:
        conn.close()


# =============================================================================
# 3. FUNGSI SINKRONISASI OTOMATIS KE FILE HTML
# =============================================================================

def sync_ke_html():
    """
    Mengambil data terbaru dari Neon PostgreSQL via get_programs(),
    lalu menuliskan langsung baris tabelnya ke dalam file public/program.html.
    """
    if not os.path.exists(HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {HTML_FILE}")

    # 1. Tarik data terbaru dari database Neon
    programs = get_programs()

    # 2. Susun template baris HTML (<tr>)
    if not programs:
        rows_html = '              <tr><td colspan="4" class="text-center py-4 text-muted">Belum ada data program di database Neon.</td></tr>\n'
    else:
        rows_list = []
        for p in programs:
            level_display = str(p.get('level') or 'SD I - VI').strip()
            level_upper = level_display.upper()
            badge_class = "badge-level"
            if "PRASEKOLAH" in level_upper or "PRA" in level_upper:
                badge_class += " badge-pra"
            elif "SMP" in level_upper:
                badge_class += " badge-smp"
            elif "SMA" in level_upper:
                badge_class += " badge-sma"
            else:
                badge_class += " badge-sd"

            p_name = str(p['name']).replace("'", "\\'")
            js_name = str(p['name']).replace("\\", "\\\\").replace("'", "\\'")
            js_level = level_display.replace("\\", "\\\\").replace("'", "\\'")
            safe_name = html_lib.escape(str(p['name']))
            safe_level = html_lib.escape(level_display)

            row = f"""              <tr>
                <td><strong>{safe_name}</strong></td>
                <td><span class="{badge_class}">{safe_level}</span></td>
                <td><span class="session-count">{p['sessions_per_month']}×</span></td>
                <td class="text-end pe-4">
                  <button type="button" class="btn-edit-pill" onclick="bukaModalEditProgram({p['id']}, '{js_name}', '{js_level}', {p['sessions_per_month']})">Edit</button>
                  <a href="?page=program.html&action=hapus&id={p['id']}&name={p_name}" target="_top" class="btn-delete-pill" style="text-decoration: none; display: inline-block;" onclick="return confirm('Yakin ingin menghapus program \'{p_name}\' dari database Neon?');">Hapus</a>
                </td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    # 3. Baca isi file program.html saat ini
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. Ganti isi antara tag penanda <!-- DATA_PROGRAM_START --> dan <!-- DATA_PROGRAM_END -->
    start_tag = '<!-- DATA_PROGRAM_START -->'
    end_tag = '<!-- DATA_PROGRAM_END -->'

    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"
    else:
        # Fallback jika penanda belum ada di tabel
        import re
        pattern = r'(<tbody id="programListBody">)(.*?)(</tbody>)'
        replacement = f'\\1\n              {start_tag}\n{rows_html}              {end_tag}\n            \\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 5. Tulis hasil kembali ke file program.html
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(programs)


def sync_tutor_ke_html():
    """
    Mengambil data terbaru dari Neon PostgreSQL via get_tutors(),
    lalu menuliskan langsung baris tabelnya ke dalam file public/tutor.html.
    """
    if not os.path.exists(TUTOR_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {TUTOR_HTML_FILE}")

    tutors = get_tutors()
    aktif_count = sum(1 for t in tutors if str(t.get('status', 'Aktif')).strip().lower() == 'aktif')

    if not tutors:
        rows_html = '              <tr><td colspan="5" class="text-center py-4 text-muted">Belum ada data tutor di database Neon.</td></tr>\n'
    else:
        rows_list = []
        for t in tutors:
            status = str(t.get('status') or 'Aktif')
            is_aktif = status.strip().lower() == 'aktif'
            badge_class = "badge-status badge-status-aktif" if is_aktif else "badge-status badge-status-nonaktif"

            safe_name = html_lib.escape(str(t['name']))
            safe_specialty = html_lib.escape(str(t['specialty']))
            safe_phone = html_lib.escape(str(t['phone']))
            safe_status = html_lib.escape(status)
            js_name = str(t['name']).replace("\\", "\\\\").replace("'", "\\'")
            js_specialty = str(t.get('specialty') or '').replace("\\", "\\\\").replace("'", "\\'")
            js_phone = str(t.get('phone') or '').replace("\\", "\\\\").replace("'", "\\'")
            js_status = str(status).replace("\\", "\\\\").replace("'", "\\'")

            row = f"""              <tr>
                <td><strong>{safe_name}</strong></td>
                <td>{safe_specialty}</td>
                <td>{safe_phone}</td>
                <td><span class="{badge_class}">{safe_status}</span></td>
                <td class="text-end pe-4">
                  <button type="button" class="btn-edit-pill" onclick="bukaModalEditTutor({int(t['id'])}, '{js_name}', '{js_specialty}', '{js_phone}', '{js_status}')">Edit</button>
                  <button type="button" class="btn-delete-pill" onclick="hapusTutor(this, '{js_name}', {int(t['id'])})">Hapus</button>
                </td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    with open(TUTOR_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_TUTOR_START -->'
    end_tag = '<!-- DATA_TUTOR_END -->'

    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"
    else:
        pattern = r'(<tbody id="tutorListBody">)(.*?)(</tbody>)'
        replacement = f'\\1\n              {start_tag}\n{rows_html}              {end_tag}\n            \\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    new_content = re.sub(
        r'(<p class="page-subtitle" id="tutorSubtitle">)(.*?)(</p>)',
        f'\\1{aktif_count} tutor aktif\\3',
        new_content,
        flags=re.DOTALL,
    )

    with open(TUTOR_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(tutors)


def sync_ruang_ke_html():
    """
    Mengambil data terbaru dari Neon PostgreSQL via get_rooms(),
    lalu menuliskan langsung grid kartu ruang belajar ke dalam file public/ruang_belajar.html.
    """
    if not os.path.exists(ROOM_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {ROOM_HTML_FILE}")

    rooms = get_rooms()

    if not rooms:
        cards_html = '        <div class="col-12"><div class="custom-card text-center text-muted py-4">Belum ada data ruang belajar di database Neon.</div></div>\n'
    else:
        cards_list = []
        for r in rooms:
            safe_name = html_lib.escape(str(r['name']))
            capacity = int(r.get('capacity') or 0)
            js_name = str(r['name']).replace("\\", "\\\\").replace("'", "\\'")

            card = f"""        <div class="col-12 col-md-4 col-lg-3">
          <div class="custom-card mb-0 h-100 d-flex flex-column justify-content-between">
            <div>
              <h5 class="fw-bold mb-2 text-dark">{safe_name}</h5>
              <p class="text-muted mb-3" style="font-size: 14.5px;">
                Kapasitas <strong>{capacity}</strong> siswa
              </p>
            </div>
            <div class="d-flex gap-2">
              <button type="button" class="btn-view-pill w-50 text-center" onclick="lihatRuang('{js_name}', {int(r['id'])})">
                Lihat
              </button>
              <button type="button" class="btn-delete-pill w-50 text-center" onclick="hapusRuang(this, '{js_name}', {int(r['id'])})">
                Hapus
              </button>
            </div>
          </div>
        </div>"""
            cards_list.append(card)
        cards_html = "\n".join(cards_list) + "\n"

    with open(ROOM_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_ROOM_START -->'
    end_tag = '<!-- DATA_ROOM_END -->'

    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = f"{before}{start_tag}\n{cards_html}        {end_tag}{after}"
    else:
        pattern = r'(<div class="row g-4" id="roomCardContainer">)(.*?)(</div>\s*</main>)'
        replacement = f'\\1\n        {start_tag}\n{cards_html}        {end_tag}\n      \\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(ROOM_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(rooms)


def sync_jadwal_ke_html():
    """
    Mengambil data jadwal terbaru dari Neon PostgreSQL via get_all_schedules(),
    lalu menuliskan langsung baris tabelnya ke dalam file public/jadwal.html.
    """
    if not os.path.exists(JADWAL_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {JADWAL_HTML_FILE}")

    schedules = get_all_schedules()

    if not schedules:
        rows_html = '              <tr><td colspan="6" class="text-center py-4 text-muted">Belum ada data jadwal di database Neon.</td></tr>\n'
    else:
        rows_list = []
        for s in schedules:
            safe_day = html_lib.escape(str(s.get('day') or '-'))
            safe_start = html_lib.escape(str(s.get('start_time') or ''))
            safe_end = html_lib.escape(str(s.get('end_time') or ''))
            safe_time = f"{safe_start}–{safe_end}"
            safe_group = html_lib.escape(str(s.get('program_name') or s.get('group_name') or '-'))
            safe_tutor = html_lib.escape(str(s.get('tutor_name') or '-'))
            safe_room = html_lib.escape(str(s.get('room_name') or '-'))
            js_info = f"{s.get('day')} - {s.get('program_name') or s.get('group_name')}".replace("\\", "\\\\").replace("'", "\\'")
            js_day = str(s.get('day') or 'Senin').replace("\\", "\\\\").replace("'", "\\'")
            prog_id = int(s.get('program_id') or 0)
            tutor_id = int(s.get('tutor_id') or 0)
            room_id = int(s.get('room_id') or 0)

            row = f"""              <tr data-hari="{safe_day}" data-ruang="{safe_room}" data-tutor="{safe_tutor}" data-waktu="{safe_time}">
                <td><strong>{safe_day}</strong></td>
                <td>{safe_time}</td>
                <td>{safe_group}</td>
                <td>{safe_tutor}</td>
                <td>{safe_room}</td>
                <td class="text-end pe-4">
                  <button type="button" class="btn-edit-pill" onclick="bukaModalEditJadwal({int(s['schedule_id'])}, '{js_day}', '{safe_start}', '{safe_end}', {prog_id}, {tutor_id}, {room_id})">Edit</button>
                  <button type="button" class="btn-delete-pill" onclick="hapusJadwal(this, '{js_info}', {int(s['schedule_id'])})">Hapus</button>
                </td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    with open(JADWAL_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_JADWAL_START -->'
    end_tag = '<!-- DATA_JADWAL_END -->'

    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"
    else:
        pattern = r'(<tbody id="scheduleListBody">)(.*?)(</tbody>)'
        replacement = f'\\1\n              {start_tag}\n{rows_html}              {end_tag}\n            \\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(JADWAL_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(schedules)


def sync_pembayaran_ke_html():
    """Menyinkronkan data tagihan & pembayaran terbaru ke public/pembayaran.html."""
    if not os.path.exists(PEMBAYARAN_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {PEMBAYARAN_HTML_FILE}")

    summary = get_billing_summary()
    bills = summary["bills"]
    stats = summary["stats"]

    if not bills:
        rows_html = '              <tr><td colspan="7" class="text-center py-4 text-muted">Belum ada data tagihan pembayaran di database Neon.</td></tr>\n'
    else:
        rows_list = []
        for b in bills:
            safe_name = html_lib.escape(b["student_name"])
            js_name = b["student_name"].replace("\\", "\\\\").replace("'", "\\'")
            btn_label = "Reset Bayar" if b["paid_amount"] > 0 else "Hapus"
            row = f"""              <tr>
                <td><strong>{safe_name}</strong></td>
                <td>{html_lib.escape(b["due_date_str"])}</td>
                <td>{format_rupiah(b["total_amount"])}</td>
                <td>{format_rupiah(b["paid_amount"])}</td>
                <td>{format_rupiah(b["remaining_amount"])}</td>
                <td><span class="{b["badge_class"]}">{html_lib.escape(b["status"])}</span></td>
                <td class="text-end pe-4">
                  <button type="button" class="btn-delete-pill" onclick="hapusPembayaran({b['bill_id']}, '{js_name}', {b['paid_amount']})">{btn_label}</button>
                </td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    options_html = "\n".join(
        f'                <option value="{b["bill_id"]}" data-sisa="{b["remaining_amount"]}">{html_lib.escape(b["student_name"])} · sisa {format_rupiah(b["remaining_amount"])}</option>'
        for b in bills
    )

    with open(PEMBAYARAN_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_PEMBAYARAN_START -->'
    end_tag = '<!-- DATA_PEMBAYARAN_END -->'
    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"

    content = re.sub(r'(<div class="stat-value" id="statLunas">)(.*?)(</div>)', f'\\1{stats["lunas"]}\\3', content, flags=re.DOTALL)
    content = re.sub(r'(<div class="stat-value" id="statBelum">)(.*?)(</div>)', f'\\1{stats["belum_lunas"]}\\3', content, flags=re.DOTALL)
    content = re.sub(r'(<div class="stat-value" id="statMenunggak">)(.*?)(</div>)', f'\\1{stats["menunggak"]}\\3', content, flags=re.DOTALL)
    content = re.sub(
        r'(<select class="form-select-custom" id="selectTagihan">)(.*?)(</select>)',
        f'\\1\n{options_html}\n              \\3',
        content,
        flags=re.DOTALL,
    )

    with open(PEMBAYARAN_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(bills)


def sync_tagihan_ke_html(period="Oktober 2026"):
    """Menyinkronkan daftar tagihan per periode ke public/tagihan.html dengan format asli (NO. TAGIHAN, SISWA, PROGRAM, PERIODE, NOMINAL)."""
    if not os.path.exists(TAGIHAN_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {TAGIHAN_HTML_FILE}")

    bills = get_bills_by_period(period)

    if not bills:
        rows_html = """              <tr id="emptyRow">
                <td colspan="5" class="text-center py-5 text-muted" style="font-size: 14.5px;">
                  Belum ada tagihan pada periode ini.
                </td>
              </tr>\n"""
    else:
        rows_list = []
        for b in bills:
            badge_status = (
                '<span class="badge-status badge-status-lunas ms-2" style="font-size: 11px; padding: 2px 10px;">Sudah Bayar</span>'
                if b["is_lunas"]
                else '<span class="badge-status badge-status-belum ms-2" style="font-size: 11px; padding: 2px 10px;">Belum Bayar</span>'
            )
            row = f"""              <tr>
                <td><code>{html_lib.escape(b["invoice_no"])}</code></td>
                <td><strong>{html_lib.escape(b["student_name"])}</strong>{badge_status}</td>
                <td>{html_lib.escape(b["program_name"])}</td>
                <td>{html_lib.escape(b.get("period") or period)}</td>
                <td class="text-end pe-4"><strong>{format_rupiah(b["total_amount"])}</strong></td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    with open(TAGIHAN_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_TAGIHAN_START -->'
    end_tag = '<!-- DATA_TAGIHAN_END -->'
    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"

    with open(TAGIHAN_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(bills)


def sync_siswa_ke_html():
    """
    Mengambil data terbaru dari Neon PostgreSQL via get_students(),
    lalu menuliskan langsung baris tabelnya ke dalam file public/siswa.html.
    """
    if not os.path.exists(SISWA_HTML_FILE):
        raise FileNotFoundError(f"File tidak ditemukan: {SISWA_HTML_FILE}")

    students = get_students()
    total_count = len(students)

    if not students:
        rows_html = '              <tr><td colspan="5" class="text-center py-4 text-muted">Belum ada data siswa di database Neon.</td></tr>\n'
    else:
        rows_list = []
        for s in students:
            lvl = str(s.get('level') or 'SD').upper()
            badge_class = "badge-level"
            if lvl == "SMP":
                badge_class += " badge-smp"
            elif lvl == "SMA":
                badge_class += " badge-sma"

            safe_name = html_lib.escape(str(s['name']))
            safe_nis = html_lib.escape(str(s.get('nis') or ''))
            safe_guardian = html_lib.escape(str(s.get('guardian_name') or '-'))
            safe_phone = html_lib.escape(str(s.get('phone') or '-'))
            js_name = str(s['name']).replace("\\", "\\\\").replace("'", "\\'")
            js_guardian = str(s.get('guardian_name') or '').replace("\\", "\\\\").replace("'", "\\'")
            js_phone = str(s.get('phone') or '').replace("\\", "\\\\").replace("'", "\\'")

            nis_badge = f' <small class="text-muted" style="font-size: 11px;">({safe_nis})</small>' if safe_nis else ''

            row = f"""              <tr>
                <td><strong>{safe_name}</strong>{nis_badge}</td>
                <td><span class="{badge_class}">{lvl}</span></td>
                <td>{safe_guardian}</td>
                <td>{safe_phone}</td>
                <td class="text-end pe-4">
                  <button type="button" class="btn-edit-pill" onclick="bukaModalEdit({int(s['id'])}, '{js_name}', '{lvl}', '{js_guardian}', '{js_phone}')">Edit</button>
                  <button type="button" class="btn-delete-pill" onclick="hapusBaris(this, '{js_name}', {int(s['id'])})">Hapus</button>
                </td>
              </tr>"""
            rows_list.append(row)
        rows_html = "\n".join(rows_list) + "\n"

    with open(SISWA_HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    start_tag = '<!-- DATA_SISWA_START -->'
    end_tag = '<!-- DATA_SISWA_END -->'

    if start_tag in content and end_tag in content:
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[1]
        new_content = f"{before}{start_tag}\n{rows_html}              {end_tag}{after}"
    else:
        pattern = r'(<tbody id="studentListBody">)(.*?)(</tbody>)'
        replacement = f'\\1\n              {start_tag}\n{rows_html}              {end_tag}\n            \\3'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    new_content = re.sub(
        r'(<p class="page-subtitle" id="totalSiswaText">)(.*?)(</p>)',
        f'\\1{total_count} siswa terdaftar\\3',
        new_content
    )

    with open(SISWA_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return total_count


# =============================================================================
# 4. HANDLER STANDBY: PENERIMA KLIK TOMBOL DARI BROWSER KE NEON
# =============================================================================

class StandbyHandler(SimpleHTTPRequestHandler):
    """Handler bawaan Python untuk mendengarkan aksi tombol Hapus / Tambah dari browser"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def end_headers(self):
        # Header CORS agar tombol berfungsi baik dibuka via file:/// maupun localhost
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)

        # 1. Endpoint Aksi Hapus Program dari Tombol di Browser
        if parsed.path == '/api/hapus':
            params = parse_qs(parsed.query)
            target = params.get('name', [None])[0] or params.get('id', [None])[0]

            if target:
                success = delete_program(target)
                sync_ke_html()
                print(f"[{time.strftime('%H:%M:%S')}] 🗑️ Tombol Hapus diklik dari browser! Berhasil menghapus program '{target}' dari Neon PostgreSQL.")
                self._send_json(200, {"success": success, "message": f"Program '{target}' dihapus"})
                return
            self._send_json(400, {"error": "Nama program tidak ditemukan"})
            return

        # 2. Endpoint Aksi Tambah Program dari Form di Browser
        elif parsed.path == '/api/tambah':
            params = parse_qs(parsed.query)
            name = params.get('name', [''])[0]
            level = params.get('level', ['SD'])[0]
            sessions = int(params.get('sessions', [8])[0])

            if name:
                new_id = add_program(name, level, sessions)
                sync_ke_html()
                print(f"[{time.strftime('%H:%M:%S')}] ➕ Program baru '{name}' ({level}) berhasil ditambahkan ke Neon PostgreSQL (ID: {new_id}).")
                self._send_json(200, {"success": True, "id": new_id})
                return

        elif parsed.path in ('/api/program/ubah', '/api/program/edit'):
            params = parse_qs(parsed.query)
            target = params.get('id', [None])[0] or params.get('name', [None])[0]
            name = params.get('name', [''])[0].strip()
            level = params.get('level', ['SD'])[0].strip()
            try:
                sessions = int(params.get('sessions', [8])[0])
            except (ValueError, TypeError):
                sessions = 8

            if target and name:
                try:
                    success = update_program(target, name, level, sessions)
                    sync_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] ✏️ Program '{target}' berhasil diperbarui ke Neon PostgreSQL ({name}, {level}, {sessions}x).")
                    self._send_json(200, {"success": success, "message": f"Program '{name}' berhasil diperbarui"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID/Nama program dan nama baru wajib diisi"})
            return

        # 3. Endpoint CRUD Tutor untuk public/tutor.html
        elif parsed.path == '/api/tutor/list':
            try:
                tutors = get_tutors()
                programs = get_programs()
                self._send_json(200, {"success": True, "tutors": tutors, "programs": programs})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/program/list':
            try:
                programs = get_programs()
                self._send_json(200, {"success": True, "programs": programs})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/tutor/tambah':
            params = parse_qs(parsed.query)
            name = params.get('name', [''])[0].strip()
            specialty = params.get('specialty', [''])[0].strip()
            phone = params.get('phone', [''])[0].strip()
            status = params.get('status', ['Aktif'])[0].strip() or 'Aktif'

            if name and specialty:
                try:
                    new_id = add_tutor(name, specialty, phone, status=status)
                    sync_tutor_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] ➕ Tutor baru '{name}' ({specialty}) berhasil ditambahkan ke Neon PostgreSQL (ID: {new_id}).")
                    self._send_json(200, {"success": True, "id": new_id})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "Nama tutor dan mata pelajaran wajib diisi"})
            return

        elif parsed.path == '/api/tutor/hapus':
            params = parse_qs(parsed.query)
            target = params.get('id', [None])[0] or params.get('name', [None])[0]

            if target:
                try:
                    success = delete_tutor(target)
                    sync_tutor_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] 🗑️ Tutor '{target}' dihapus dari Neon PostgreSQL.")
                    self._send_json(200, {"success": success, "message": f"Tutor '{target}' dihapus"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID atau nama tutor tidak ditemukan"})
            return

        elif parsed.path in ('/api/tutor/ubah', '/api/tutor/edit'):
            params = parse_qs(parsed.query)
            t_id = params.get('id', [None])[0]
            name = params.get('name', [''])[0].strip()
            specialty = params.get('specialty', [''])[0].strip()
            phone = params.get('phone', [''])[0].strip()
            status = params.get('status', ['Aktif'])[0].strip() or 'Aktif'

            if t_id and name and specialty:
                try:
                    success = update_tutor(int(t_id), name, specialty, phone, status=status)
                    sync_tutor_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] ✏️ Tutor ID {t_id} ('{name}') berhasil diperbarui di Neon PostgreSQL.")
                    self._send_json(200, {"success": success, "message": f"Tutor '{name}' berhasil diperbarui"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID tutor, nama, dan bidang wajib diisi"})
            return

        # 4. Endpoint CRUD Ruang Belajar untuk public/ruang_belajar.html
        elif parsed.path == '/api/ruang/list':
            try:
                rooms = get_rooms()
                self._send_json(200, {"success": True, "rooms": rooms})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/ruang/tambah':
            params = parse_qs(parsed.query)
            name = params.get('name', [''])[0].strip()
            try:
                capacity = int(params.get('capacity', [5])[0])
            except (TypeError, ValueError):
                capacity = 5

            if name and capacity >= 1:
                try:
                    new_id = add_room(name, capacity)
                    sync_ruang_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] ➕ Ruang '{name}' (kapasitas {capacity}) berhasil ditambahkan ke Neon PostgreSQL (ID: {new_id}).")
                    self._send_json(200, {"success": True, "id": new_id})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "Nama ruang dan kapasitas valid wajib diisi"})
            return

        elif parsed.path == '/api/ruang/hapus':
            params = parse_qs(parsed.query)
            target = params.get('id', [None])[0] or params.get('name', [None])[0]

            if target:
                try:
                    success = delete_room(target)
                    sync_ruang_ke_html()
                    sync_jadwal_ke_html()
                    print(f"[{time.strftime('%H:%M:%S')}] 🗑️ Ruang '{target}' dihapus dari Neon PostgreSQL.")
                    self._send_json(200, {"success": success, "message": f"Ruang '{target}' dihapus"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID atau nama ruang tidak ditemukan"})
            return

        elif parsed.path == '/api/ruang/jadwal':
            params = parse_qs(parsed.query)
            room_id = params.get('room_id', [None])[0]
            if not room_id or not str(room_id).isdigit():
                self._send_json(400, {"success": False, "error": "room_id tidak valid"})
                return
            try:
                rooms = get_rooms()
                room_info = next((r for r in rooms if int(r["id"]) == int(room_id)), None)
                schedules = get_room_schedules(int(room_id))
                tutors = get_tutors()
                programs = get_programs()
                self._send_json(200, {
                    "success": True,
                    "room": room_info,
                    "schedules": schedules,
                    "tutors": tutors,
                    "programs": programs,
                })
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/ruang/jadwal/tambah':
            params = parse_qs(parsed.query)
            room_id = params.get('room_id', [None])[0]
            tutor_id = params.get('tutor_id', [None])[0]
            program_id = params.get('program_id', [None])[0]
            group_name = params.get('group_name', [None])[0]
            day = params.get('day', ['Senin'])[0].strip() or 'Senin'
            start_time = params.get('start_time', ['15:00'])[0].strip() or '15:00'
            end_time = params.get('end_time', ['16:30'])[0].strip() or '16:30'

            if not room_id or not str(room_id).isdigit():
                self._send_json(400, {"success": False, "error": "room_id wajib valid"})
                return
            try:
                sched_id = add_room_schedule(
                    int(room_id),
                    int(tutor_id) if tutor_id and str(tutor_id).isdigit() else None,
                    int(program_id) if program_id and str(program_id).isdigit() else None,
                    day,
                    start_time,
                    end_time,
                    group_name=group_name,
                )
                sync_jadwal_ke_html()
                self._send_json(200, {"success": True, "id": sched_id})
            except ValueError as e:
                self._send_json(409, {"success": False, "error": str(e)})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/ruang/jadwal/hapus':
            params = parse_qs(parsed.query)
            sched_id = params.get('id', [None])[0]
            if not sched_id or not str(sched_id).isdigit():
                self._send_json(400, {"success": False, "error": "id jadwal tidak valid"})
                return
            try:
                success = delete_room_schedule(int(sched_id))
                sync_jadwal_ke_html()
                self._send_json(200, {"success": success})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        # 5. Endpoint CRUD Jadwal Terpadu untuk public/jadwal.html
        elif parsed.path == '/api/jadwal/list':
            try:
                schedules = get_all_schedules()
                programs = get_programs()
                tutors = get_tutors()
                rooms = get_rooms()
                self._send_json(200, {
                    "success": True,
                    "schedules": schedules,
                    "programs": programs,
                    "tutors": tutors,
                    "rooms": rooms,
                })
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/jadwal/tambah':
            params = parse_qs(parsed.query)
            room_id = params.get('room_id', [None])[0]
            tutor_id = params.get('tutor_id', [None])[0]
            program_id = params.get('program_id', [None])[0]
            group_name = params.get('group_name', [None])[0]
            day = params.get('day', ['Senin'])[0].strip() or 'Senin'
            start_time = params.get('start_time', ['15:00'])[0].strip() or '15:00'
            end_time = params.get('end_time', ['16:30'])[0].strip() or '16:30'

            if not room_id or not str(room_id).isdigit() or not tutor_id or not str(tutor_id).isdigit():
                self._send_json(400, {"success": False, "error": "Ruang dan Tutor wajib dipilih"})
                return
            try:
                sched_id = add_schedule(
                    int(room_id),
                    int(tutor_id),
                    int(program_id) if program_id and str(program_id).isdigit() else None,
                    day,
                    start_time,
                    end_time,
                    group_name=group_name,
                )
                sync_jadwal_ke_html()
                self._send_json(200, {"success": True, "id": sched_id})
            except ValueError as e:
                self._send_json(409, {"success": False, "error": str(e)})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/jadwal/hapus':
            params = parse_qs(parsed.query)
            sched_id = params.get('id', [None])[0]
            if not sched_id or not str(sched_id).isdigit():
                self._send_json(400, {"success": False, "error": "id jadwal tidak valid"})
                return
            try:
                success = delete_schedule(int(sched_id))
                sync_jadwal_ke_html()
                self._send_json(200, {"success": success})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path in ('/api/jadwal/ubah', '/api/jadwal/edit'):
            params = parse_qs(parsed.query)
            sched_id = params.get('id', [None])[0]
            room_id = params.get('room_id', [None])[0]
            tutor_id = params.get('tutor_id', [None])[0]
            program_id = params.get('program_id', [None])[0]
            group_name = params.get('group_name', [None])[0]
            day = params.get('day', ['Senin'])[0].strip() or 'Senin'
            start_time = params.get('start_time', ['15:00'])[0].strip() or '15:00'
            end_time = params.get('end_time', ['16:30'])[0].strip() or '16:30'

            if not sched_id or not str(sched_id).isdigit():
                self._send_json(400, {"success": False, "error": "id jadwal tidak valid"})
                return
            if not room_id or not str(room_id).isdigit() or not tutor_id or not str(tutor_id).isdigit():
                self._send_json(400, {"success": False, "error": "Ruang dan Tutor wajib dipilih"})
                return
            try:
                success = update_schedule(
                    int(sched_id),
                    int(room_id),
                    int(tutor_id),
                    int(program_id) if program_id and str(program_id).isdigit() else None,
                    day,
                    start_time,
                    end_time,
                    group_name=group_name,
                )
                sync_jadwal_ke_html()
                print(f"[{time.strftime('%H:%M:%S')}] ✏️ Jadwal ID {sched_id} berhasil diperbarui di Neon PostgreSQL.")
                self._send_json(200, {"success": success, "message": f"Jadwal ID {sched_id} berhasil diperbarui"})
            except ValueError as e:
                self._send_json(409, {"success": False, "error": str(e)})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/jadwal/cek_bentrok':
            params = parse_qs(parsed.query)
            day = params.get('day', ['Selasa'])[0].strip() or 'Selasa'
            start_time = params.get('start_time', ['15:30'])[0].strip()
            end_time = params.get('end_time', ['17:00'])[0].strip()
            room_id = params.get('room_id', [None])[0]
            tutor_id = params.get('tutor_id', [None])[0]

            res = check_conflict(
                day,
                start_time,
                end_time,
                room_id=int(room_id) if room_id and str(room_id).isdigit() else None,
                tutor_id=int(tutor_id) if tutor_id and str(tutor_id).isdigit() else None,
            )
            self._send_json(200, {"success": True, **res})
            return

        # 6. Endpoint CRUD Pembayaran & Read Tagihan (pembayaran.html & tagihan.html)
        elif parsed.path == '/api/pembayaran/list':
            try:
                summary = get_billing_summary()
                self._send_json(200, {"success": True, **summary})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/tagihan/list':
            params = parse_qs(parsed.query)
            periode = params.get('periode', [None])[0]
            try:
                if periode:
                    bills = get_bills_by_period(periode)
                    self._send_json(200, {"success": True, "bills": bills, "periode": periode})
                else:
                    summary = get_billing_summary()
                    self._send_json(200, {"success": True, **summary})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/tagihan/terbitkan':
            params = parse_qs(parsed.query)
            periode = params.get('periode', ['Oktober 2026'])[0].strip() or 'Oktober 2026'
            try:
                bills = publish_bills_for_period(periode)
                sync_tagihan_ke_html(periode)
                sync_pembayaran_ke_html()
                self._send_json(200, {"success": True, "bills": bills, "periode": periode})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/pembayaran/catat':
            params = parse_qs(parsed.query)
            bill_id = params.get('bill_id', [None])[0]
            amount = params.get('amount', [0])[0]
            method = params.get('method', ['Transfer Bank'])[0]
            if not bill_id or not str(bill_id).isdigit():
                self._send_json(400, {"success": False, "error": "Tagihan wajib dipilih"})
                return
            try:
                pay_id = add_payment(int(bill_id), amount, payment_method=method)
                sync_pembayaran_ke_html()
                sync_tagihan_ke_html()
                self._send_json(200, {"success": True, "id": pay_id})
            except ValueError as e:
                self._send_json(400, {"success": False, "error": str(e)})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/pembayaran/tambah_tagihan':
            params = parse_qs(parsed.query)
            student_name = params.get('student_name', [''])[0].strip()
            program_name = params.get('program_name', ['Bimbel'])[0].strip()
            amount = params.get('amount', [0])[0]
            due_date = params.get('due_date', [None])[0]
            try:
                b_id = add_bill(student_name, program_name, amount, due_date=due_date)
                sync_pembayaran_ke_html()
                sync_tagihan_ke_html()
                self._send_json(200, {"success": True, "id": b_id})
            except ValueError as e:
                self._send_json(400, {"success": False, "error": str(e)})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/pembayaran/hapus':
            params = parse_qs(parsed.query)
            bill_id = params.get('bill_id', [None])[0]
            if not bill_id or not str(bill_id).isdigit():
                self._send_json(400, {"success": False, "error": "bill_id tidak valid"})
                return
            try:
                action_type = delete_bill_payment(int(bill_id))
                sync_pembayaran_ke_html()
                sync_tagihan_ke_html()
                self._send_json(200, {"success": True, "action": action_type})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        # 7. Endpoint CRUD Siswa untuk public/siswa.html
        elif parsed.path == '/api/siswa/list':
            try:
                students = get_students()
                self._send_json(200, {"success": True, "students": students})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif parsed.path == '/api/siswa/tambah':
            params = parse_qs(parsed.query)
            name = params.get('name', [''])[0].strip()
            level = params.get('level', ['SD'])[0].strip() or 'SD'
            guardian = params.get('guardian_name', ['-'])[0].strip() or '-'
            phone = params.get('phone', ['-'])[0].strip() or '-'
            gender = params.get('gender', ['L'])[0].strip() or 'L'
            status = params.get('status', ['Aktif'])[0].strip() or 'Aktif'
            nis = params.get('nis', [None])[0]

            if name:
                try:
                    new_id = add_student(name, level=level, guardian_name=guardian, phone=phone, gender=gender, nis=nis, status=status)
                    try:
                        sync_siswa_ke_html()
                    except Exception:
                        pass
                    print(f"[{time.strftime('%H:%M:%S')}] ➕ Siswa baru '{name}' ({level}) berhasil ditambahkan ke Neon PostgreSQL (ID: {new_id}).")
                    self._send_json(200, {"success": True, "id": new_id})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "Nama siswa wajib diisi"})
            return

        elif parsed.path == '/api/siswa/ubah' or parsed.path == '/api/siswa/edit':
            params = parse_qs(parsed.query)
            s_id = params.get('id', [None])[0]
            name = params.get('name', [None])[0]
            level = params.get('level', [None])[0]
            guardian = params.get('guardian_name', [None])[0]
            phone = params.get('phone', [None])[0]
            status = params.get('status', [None])[0]
            gender = params.get('gender', [None])[0]
            nis = params.get('nis', [None])[0]

            if s_id and str(s_id).isdigit():
                try:
                    success = update_student(
                        int(s_id),
                        name=name,
                        level=level,
                        guardian_name=guardian,
                        phone=phone,
                        status=status,
                        gender=gender,
                        nis=nis,
                    )
                    try:
                        sync_siswa_ke_html()
                    except Exception:
                        pass
                    print(f"[{time.strftime('%H:%M:%S')}] ✏️ Siswa ID {s_id} berhasil diperbarui di Neon PostgreSQL.")
                    self._send_json(200, {"success": success, "message": f"Siswa ID {s_id} diperbarui"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID siswa valid wajib diisi"})
            return

        elif parsed.path == '/api/siswa/hapus':
            params = parse_qs(parsed.query)
            target = params.get('id', [None])[0] or params.get('name', [None])[0]

            if target:
                try:
                    success = delete_student(target)
                    try:
                        sync_siswa_ke_html()
                    except Exception:
                        pass
                    print(f"[{time.strftime('%H:%M:%S')}] 🗑️ Siswa '{target}' dihapus dari Neon PostgreSQL.")
                    self._send_json(200, {"success": success, "message": f"Siswa '{target}' dihapus"})
                except Exception as e:
                    self._send_json(500, {"success": False, "error": str(e)})
                return
            self._send_json(400, {"success": False, "error": "ID atau nama siswa tidak ditemukan"})
            return

        # 8. Default: sajikan file HTML/CSS/JS
        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        if self.headers.get('Content-Type', '').startswith('application/json') and body:
            try:
                data = json.loads(body)
                from urllib.parse import urlencode
                query_str = urlencode({k: str(v) for k, v in data.items()})
                self.path = f"{self.path.split('?')[0]}?{query_str}"
            except Exception:
                pass
        elif body and '=' in body:
            self.path = f"{self.path.split('?')[0]}?{body}"
        return self.do_GET()

    def log_message(self, format, *args):
        # Meredam log HTTP default agar tampilan terminal tetap bersih
        return


def start_standby_mode(port=8000):
    """
    Menjalankan database.py dalam mode STANDBY / SIAGA.
    database.py akan terus aktif mendengarkan perintah dari browser (seperti tombol Hapus),
    sekaligus otomatis memperbarui data di Neon PostgreSQL!
    """
    # 1. Sinkronisasi awal ke HTML
    try:
        total = sync_ke_html()
        total_tutors = sync_tutor_ke_html()
        total_rooms = sync_ruang_ke_html()
        total_jadwal = sync_jadwal_ke_html()
        total_bayar = sync_pembayaran_ke_html()
        sync_tagihan_ke_html()
        total_students = sync_siswa_ke_html()
        print(f"[{time.strftime('%H:%M:%S')}] ✓ Sinkronisasi awal sukses. Total: {total} program, {total_tutors} tutor, {total_rooms} ruang, {total_jadwal} jadwal, {total_students} siswa, {total_bayar} tagihan.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ! Peringatan sinkronisasi awal: {e}")

    # 2. Jalankan listener standby di port 8000
    HTTPServer.allow_reuse_address = True
    try:
        server = HTTPServer(('0.0.0.0', port), StandbyHandler)
    except OSError:
        # Fallback jika port 8000 terpakai
        port = 8080
        server = HTTPServer(('0.0.0.0', port), StandbyHandler)

    print("\n" + "=" * 60)
    print("   [STANDBY MODE] DATABASE.PY AKTIF & SIAGA DI TERMINAL")
    print("=" * 60)
    print(f"✓ Status: STANDBY di port {port}")
    print(f"✓ Tombol Hapus di browser kini TERHUBUNG LANGSUNG ke Neon!")
    print(f"✓ Akses web: http://localhost:{port}/program.html")
    print("✓ Tekan [CTRL + C] di terminal jika ingin menghentikan standby.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Mode standby dihentikan. database.py selesai.")
    finally:
        server.server_close()


# =============================================================================
# 5. RUNNER CLI INTERAKTIF (python database.py)
# =============================================================================
if __name__ == '__main__':
    args = sys.argv[1:]

    # OPSI 1: MODE STANDBY -> python database.py standby
    if len(args) >= 1 and args[0].lower() in ['standby', 'watch', 'monitor', 'live']:
        start_standby_mode(port=8000)

    # OPSI 2: Hapus data langsung lewat terminal -> python database.py hapus <nama/id>
    elif len(args) >= 2 and args[0].lower() in ['hapus', 'delete']:
        target = args[1]
        print(f"\nMenghapus program '{target}' dari database Neon...")
        if delete_program(target):
            print(f"✓ Berhasil menghapus program '{target}' dari database Neon.")
        else:
            print(f"! Program '{target}' tidak ditemukan di database.")
        print("\nMelakukan sinkronisasi ulang ke public/program.html...")
        total = sync_ke_html()
        print(f"✓ Selesai! public/program.html berhasil diperbarui (Total: {total} program).")

    # OPSI 3: Tambah data lewat terminal -> python database.py tambah "Nama" Jenjang Sesi
    elif len(args) >= 3 and args[0].lower() in ['tambah', 'add']:
        nama = args[1]
        jenjang = args[2]
        sesi = int(args[3]) if len(args) > 3 else 8
        print(f"\nMenambahkan program '{nama}' ({jenjang}, {sesi}x) ke database Neon...")
        new_id = add_program(nama, jenjang, sesi)
        print(f"✓ Sukses menambahkan program! ID baru: {new_id}")
        print("\nMelakukan sinkronisasi ke public/program.html...")
        total = sync_ke_html()
        print(f"✓ Selesai! public/program.html berhasil diperbarui (Total: {total} program).")

    # OPSI 4: Default (python database.py) -> Tes koneksi & Sync 1x
    else:
        print("=" * 60)
        print("   OPTIMATIKA - PENGELOLAAN DATABASE NEON & SYNC HTML")
        print("=" * 60)
        try:
            print("\n1. Menguji koneksi ke Neon PostgreSQL...")
            conn = create_new_connection()
            print("✓ Sukses terhubung ke database Neon PostgreSQL!")
            conn.close()

            print("\n2. Melakukan sinkronisasi data ke semua file HTML...")
            total = sync_ke_html()
            total_tutors = sync_tutor_ke_html()
            total_rooms = sync_ruang_ke_html()
            total_jadwal = sync_jadwal_ke_html()
            total_bayar = sync_pembayaran_ke_html()
            sync_tagihan_ke_html()
            print(f"✓ Sukses! program ({total}), tutor ({total_tutors}), ruang ({total_rooms}), jadwal ({total_jadwal}), tagihan/pembayaran ({total_bayar}) berhasil diperbarui.")

            print("\n3. Daftar Program Belajar Saat Ini:")
            programs = get_programs()
            print("   " + "-" * 52)
            print(f"   {'ID':<5} | {'NAMA PROGRAM':<22} | {'JENJANG':<8} | {'PERTEMUAN'}")
            print("   " + "-" * 52)
            for p in programs:
                print(f"   {p['id']:<5} | {p['name']:<22} | {p['level']:<8} | {p['sessions_per_month']}x / bulan")
            print("   " + "-" * 52)

            print("\n💡 Tips:")
            print(" • Agar tombol Hapus di browser AKTIF : python database.py standby")
            print(" • Tambah program lewat terminal     : python database.py tambah \"Nama Program\" Jenjang Pertemuan")
            print(" • Hapus program lewat terminal      : python database.py hapus \"Nama Program\"")
            print("=" * 60)

        except Exception as e:
            print(f"\n✗ Terjadi kendala: {e}")
