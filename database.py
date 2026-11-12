from datetime import datetime, timezone, timedelta
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


# =============================================================================
# 2B. FUNGSI PENGELOLAAN DATA TUTOR (CRUD)
# =============================================================================

def get_tutors():
    """Mengambil semua daftar tutor dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        if PSYCOPG_V3:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC;")
                return cur.fetchall()
        else:
            with conn.cursor(cursor_factory=psycopg.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC;")
                return [dict(r) for r in cur.fetchall()]
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


def _check_schedule_conflict(cur, day, start_time, end_time, room_id=None, tutor_id=None):
    """Memeriksa bentrok ruang maupun bentrok tutor pada hari yang sama dengan irisan jam."""
    if room_id:
        cur.execute(
            """
            SELECT COALESCE(r.name, 'Ruang'), s.start_time, s.end_time, COALESCE(p.name, sg.name)
            FROM schedules s
            JOIN study_groups sg ON s.study_group_id = sg.id
            LEFT JOIN rooms r ON sg.room_id = r.id
            LEFT JOIN programs p ON sg.program_id = p.id
            WHERE LOWER(s.day) = LOWER(%s)
              AND sg.room_id = %s
              AND s.start_time < %s
              AND %s < s.end_time
            LIMIT 1;
            """,
            (day, int(room_id), end_time, start_time),
        )
        room_hit = cur.fetchone()
        if room_hit:
            raise ValueError(
                f"JADWAL BENTROK! {room_hit[0]} sudah digunakan kelas {room_hit[3]} "
                f"pada hari {day} pukul {room_hit[1]}–{room_hit[2]}."
            )

    if tutor_id:
        cur.execute(
            """
            SELECT COALESCE(t.name, 'Tutor'), s.start_time, s.end_time, COALESCE(r.name, 'Ruang')
            FROM schedules s
            JOIN study_groups sg ON s.study_group_id = sg.id
            LEFT JOIN tutors t ON sg.tutor_id = t.id
            LEFT JOIN rooms r ON sg.room_id = r.id
            WHERE LOWER(s.day) = LOWER(%s)
              AND sg.tutor_id = %s
              AND s.start_time < %s
              AND %s < s.end_time
            LIMIT 1;
            """,
            (day, int(tutor_id), end_time, start_time),
        )
        tutor_hit = cur.fetchone()
        if tutor_hit:
            raise ValueError(
                f"TUTOR BENTROK! {tutor_hit[0]} sudah mengajar di {tutor_hit[3]} "
                f"pada hari {day} pukul {tutor_hit[1]}–{tutor_hit[2]}."
            )


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
            level = str(p.get('level', 'SD')).upper()
            badge_class = "badge-level"
            if level == "SMP":
                badge_class += " badge-smp"
            elif level == "SMA":
                badge_class += " badge-sma"

            p_name = p['name'].replace("'", "\\'")

            row = f"""              <tr>
                <td><strong>{p['name']}</strong></td>
                <td><span class="{badge_class}">{level}</span></td>
                <td><span class="session-count">{p['sessions_per_month']}×</span></td>
                <td class="text-end pe-4">
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

            row = f"""              <tr>
                <td><strong>{safe_name}</strong></td>
                <td>{safe_specialty}</td>
                <td>{safe_phone}</td>
                <td><span class="{badge_class}">{safe_status}</span></td>
                <td class="text-end pe-4">
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
            safe_time = f"{html_lib.escape(str(s.get('start_time') or ''))}–{html_lib.escape(str(s.get('end_time') or ''))}"
            safe_group = html_lib.escape(str(s.get('program_name') or s.get('group_name') or '-'))
            safe_tutor = html_lib.escape(str(s.get('tutor_name') or '-'))
            safe_room = html_lib.escape(str(s.get('room_name') or '-'))
            js_info = f"{s.get('day')} - {s.get('program_name') or s.get('group_name')}".replace("\\", "\\\\").replace("'", "\\'")

            row = f"""              <tr data-hari="{safe_day}" data-ruang="{safe_room}" data-tutor="{safe_tutor}" data-waktu="{safe_time}">
                <td><strong>{safe_day}</strong></td>
                <td>{safe_time}</td>
                <td>{safe_group}</td>
                <td>{safe_tutor}</td>
                <td>{safe_room}</td>
                <td class="text-end pe-4">
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

        # 3. Endpoint CRUD Tutor untuk public/tutor.html
        elif parsed.path == '/api/tutor/list':
            try:
                tutors = get_tutors()
                self._send_json(200, {"success": True, "tutors": tutors})
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

        # 6. Default: sajikan file HTML/CSS/JS
        super().do_GET()

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
        print(f"[{time.strftime('%H:%M:%S')}] ✓ Sinkronisasi awal sukses. Total: {total} program, {total_tutors} tutor, {total_rooms} ruang, {total_jadwal} jadwal di database.")
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

            print("\n2. Melakukan sinkronisasi data ke public/program.html, public/tutor.html, public/ruang_belajar.html, & public/jadwal.html...")
            total = sync_ke_html()
            total_tutors = sync_tutor_ke_html()
            total_rooms = sync_ruang_ke_html()
            total_jadwal = sync_jadwal_ke_html()
            print(f"✓ Sukses! program ({total}), tutor ({total_tutors}), ruang ({total_rooms}), jadwal ({total_jadwal}) berhasil diperbarui.")

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
