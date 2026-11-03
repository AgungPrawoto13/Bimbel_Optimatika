#!/usr/bin/env python3
"""
Optimatika Admin Bimbel Backend Server
Mendukung:
1. Neon PostgreSQL (via DATABASE_URL dengan psycopg2 atau pg8000)
2. SQLite (Fallback otomatis jika Neon belum dikonfigurasi / offline)
3. REST API untuk Program Belajar, Siswa, Tutor, Ruangan, Jadwal, Tagihan & Pembayaran
"""

import os
import sys
import json
import sqlite3
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

# Coba muat .env secara mandiri tanpa library eksternal
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

DATABASE_URL = os.environ.get('DATABASE_URL', '')
PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
SQLITE_DB = os.path.join(BASE_DIR, 'optimatika.db')

# Coba import driver postgres jika ada
PSYCOPG2_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class DatabaseManager:
    def __init__(self):
        self.use_postgres = False
        self.db_url = DATABASE_URL
        self.last_error = None
        self.check_connection()

    def check_connection(self):
        self.db_url = os.environ.get('DATABASE_URL', self.db_url)
        if self.db_url and PSYCOPG2_AVAILABLE:
            try:
                conn = psycopg2.connect(self.db_url, connect_timeout=5)
                conn.close()
                self.use_postgres = True
                self.last_error = None
                print("✓ Terhubung ke Neon PostgreSQL!")
                self.init_postgres_tables()
                return True
            except Exception as e:
                self.last_error = str(e)
                print(f"! Gagal konek ke PostgreSQL ({e}), beralih ke SQLite lokal.")
                self.use_postgres = False
        else:
            self.use_postgres = False
        
        self.init_sqlite_tables()
        return False

    def get_postgres_connection(self):
        return psycopg2.connect(self.db_url)

    def get_sqlite_connection(self):
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn

    def init_sqlite_tables(self):
        conn = self.get_sqlite_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                level TEXT NOT NULL,
                sessions_per_month INTEGER NOT NULL DEFAULT 8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tutors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                status TEXT DEFAULT 'Aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 10,
                facilities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nis TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                guardian_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                program_id INTEGER,
                status TEXT DEFAULT 'Aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE SET NULL
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS study_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                program_id INTEGER,
                tutor_id INTEGER,
                room_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_group_id INTEGER,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                student_id INTEGER,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'Belum Lunas',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_no TEXT UNIQUE NOT NULL,
                bill_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'Transfer Bank',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Cek apakah data programs masih kosong, jika ya isi data bawaan seperti gambar
        cur.execute("SELECT COUNT(*) FROM programs")
        count = cur.fetchone()[0]
        if count == 0:
            default_programs = [
                ('Calistung', 'SD', 8),
                ('Matematika SD', 'SD', 8),
                ('Matematika SMP', 'SMP', 8),
                ('IPA Terpadu', 'SMP', 8),
                ('Persiapan UTBK', 'SMA', 12)
            ]
            cur.executemany("INSERT INTO programs (name, level, sessions_per_month) VALUES (?, ?, ?)", default_programs)
            
            # Seed tutors
            cur.executemany("INSERT INTO tutors (name, specialty, phone, email, status) VALUES (?, ?, ?, ?, ?)", [
                ('Kak Budi Santoso, S.Pd.', 'Matematika SD & SMP', '081234567890', 'budi@optimatika.id', 'Aktif'),
                ('Kak Siti Aminah, M.Si.', 'IPA Terpadu & Fisika', '081298765432', 'siti@optimatika.id', 'Aktif'),
                ('Kak Rizky Pratama, S.Si.', 'Matematika Saintek / UTBK', '085712345678', 'rizky@optimatika.id', 'Aktif')
            ])

            # Seed rooms
            cur.executemany("INSERT INTO rooms (name, capacity, facilities) VALUES (?, ?, ?)", [
                ('Ruang Alpha (Lt. 1)', 8, 'AC, Smart Board, Dispenser'),
                ('Ruang Beta (Lt. 1)', 10, 'AC, Whiteboard, Modul Lengkap'),
                ('Ruang Gamma (Lt. 2)', 12, 'AC, Projector, Sound System')
            ])

            # Seed students
            cur.executemany("INSERT INTO students (nis, name, gender, guardian_name, phone, program_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", [
                ('OPT-2026-001', 'Ahmad Farhan', 'L', 'Bpk. Hendra', '081211112222', 1, 'Aktif'),
                ('OPT-2026-002', 'Nabila Putri', 'P', 'Ibu Ratna', '081333334444', 2, 'Aktif'),
                ('OPT-2026-003', 'Dimas Anggara', 'L', 'Bpk. Bambang', '085655556666', 3, 'Aktif'),
                ('OPT-2026-004', 'Zahra Amelia', 'P', 'Ibu Dewi', '087777778888', 5, 'Aktif')
            ])

        conn.commit()
        conn.close()

    def init_postgres_tables(self):
        conn = self.get_postgres_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                level VARCHAR(20) NOT NULL,
                sessions_per_month INTEGER NOT NULL DEFAULT 8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tutors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                specialty VARCHAR(100) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                email VARCHAR(100),
                status VARCHAR(20) DEFAULT 'Aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 10,
                facilities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                nis VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(150) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                guardian_name VARCHAR(150) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
                status VARCHAR(20) DEFAULT 'Aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS study_groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
                tutor_id INTEGER REFERENCES tutors(id) ON DELETE SET NULL,
                room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS schedules (
                id SERIAL PRIMARY KEY,
                study_group_id INTEGER REFERENCES study_groups(id) ON DELETE CASCADE,
                day VARCHAR(20) NOT NULL,
                start_time VARCHAR(10) NOT NULL,
                end_time VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS bills (
                id SERIAL PRIMARY KEY,
                invoice_no VARCHAR(50) UNIQUE NOT NULL,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                amount NUMERIC(12, 2) NOT NULL,
                due_date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'Belum Lunas',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
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
        ''')
        
        # Cek data programs
        cur.execute("SELECT COUNT(*) FROM programs")
        count = cur.fetchone()[0]
        if count == 0:
            default_programs = [
                ('Calistung', 'SD', 8),
                ('Matematika SD', 'SD', 8),
                ('Matematika SMP', 'SMP', 8),
                ('IPA Terpadu', 'SMP', 8),
                ('Persiapan UTBK', 'SMA', 12)
            ]
            for p in default_programs:
                cur.execute("INSERT INTO programs (name, level, sessions_per_month) VALUES (%s, %s, %s)", p)

            # Seed tutors
            tutors = [
                ('Kak Budi Santoso, S.Pd.', 'Matematika SD & SMP', '081234567890', 'budi@optimatika.id', 'Aktif'),
                ('Kak Siti Aminah, M.Si.', 'IPA Terpadu & Fisika', '081298765432', 'siti@optimatika.id', 'Aktif'),
                ('Kak Rizky Pratama, S.Si.', 'Matematika Saintek / UTBK', '085712345678', 'rizky@optimatika.id', 'Aktif')
            ]
            for t in tutors:
                cur.execute("INSERT INTO tutors (name, specialty, phone, email, status) VALUES (%s, %s, %s, %s, %s)", t)

            # Seed rooms
            rooms = [
                ('Ruang Alpha (Lt. 1)', 8, 'AC, Smart Board, Dispenser'),
                ('Ruang Beta (Lt. 1)', 10, 'AC, Whiteboard, Modul Lengkap'),
                ('Ruang Gamma (Lt. 2)', 12, 'AC, Projector, Sound System')
            ]
            for r in rooms:
                cur.execute("INSERT INTO rooms (name, capacity, facilities) VALUES (%s, %s, %s)", r)

        conn.commit()
        conn.close()

    def query(self, sql_pg, sql_sqlite, params=()):
        if self.use_postgres:
            conn = self.get_postgres_connection()
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(sql_pg, params)
                    if cur.description:
                        rows = cur.fetchall()
                        result = [dict(r) for r in rows]
                    else:
                        result = []
                conn.commit()
                return result
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute(sql_sqlite, params)
                if cur.description:
                    rows = cur.fetchall()
                    result = [dict(r) for r in rows]
                else:
                    result = []
                conn.commit()
                return result
            finally:
                conn.close()

    def execute_insert(self, sql_pg, sql_sqlite, params=()):
        if self.use_postgres:
            conn = self.get_postgres_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(sql_pg, params)
                    inserted_id = cur.fetchone()[0] if 'RETURNING id' in sql_pg.upper() else None
                conn.commit()
                return inserted_id
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cur = conn.cursor()
                cur.execute(sql_sqlite, params)
                inserted_id = cur.lastrowid
                conn.commit()
                return inserted_id
            finally:
                conn.close()


db = DatabaseManager()


class AdminRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def _parse_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                return json.loads(body)
            except Exception:
                return {}
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, 'application/json')
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Static files
        if not path.startswith('/api'):
            if path == '/' or path == '':
                filepath = os.path.join(PUBLIC_DIR, 'index.html')
            else:
                filepath = os.path.join(PUBLIC_DIR, path.lstrip('/'))

            if os.path.exists(filepath) and os.path.isfile(filepath):
                mime, _ = mimetypes.guess_type(filepath)
                self._set_headers(200, mime or 'text/plain')
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                # Fallback to index.html for SPA-like routes
                fallback = os.path.join(PUBLIC_DIR, 'index.html')
                if os.path.exists(fallback):
                    self._set_headers(200, 'text/html')
                    with open(fallback, 'rb') as f:
                        self.wfile.write(f.read())
                    return
                self._send_json({"error": "File not found"}, 404)
                return

        # API Endpoints
        try:
            if path == '/api/status':
                self._send_json({
                    "status": "online",
                    "database": "Neon PostgreSQL" if db.use_postgres else "SQLite (Lokal)",
                    "using_postgres": db.use_postgres,
                    "psycopg2_installed": PSYCOPG2_AVAILABLE,
                    "has_database_url": bool(os.environ.get('DATABASE_URL')),
                    "last_error": db.last_error
                })
                return

            elif path == '/api/programs':
                rows = db.query(
                    "SELECT id, name, level, sessions_per_month, created_at FROM programs ORDER BY id ASC",
                    "SELECT id, name, level, sessions_per_month, created_at FROM programs ORDER BY id ASC"
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/students':
                rows = db.query(
                    """SELECT s.id, s.nis, s.name, s.gender, s.guardian_name, s.phone, s.status, 
                              s.program_id, p.name as program_name, p.level as program_level
                       FROM students s 
                       LEFT JOIN programs p ON s.program_id = p.id 
                       ORDER BY s.id DESC""",
                    """SELECT s.id, s.nis, s.name, s.gender, s.guardian_name, s.phone, s.status, 
                              s.program_id, p.name as program_name, p.level as program_level
                       FROM students s 
                       LEFT JOIN programs p ON s.program_id = p.id 
                       ORDER BY s.id DESC"""
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/tutors':
                rows = db.query(
                    "SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC",
                    "SELECT id, name, specialty, phone, email, status FROM tutors ORDER BY id ASC"
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/rooms':
                rows = db.query(
                    "SELECT id, name, capacity, facilities FROM rooms ORDER BY id ASC",
                    "SELECT id, name, capacity, facilities FROM rooms ORDER BY id ASC"
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/groups':
                rows = db.query(
                    """SELECT g.id, g.name, p.name as program_name, t.name as tutor_name, r.name as room_name
                       FROM study_groups g
                       LEFT JOIN programs p ON g.program_id = p.id
                       LEFT JOIN tutors t ON g.tutor_id = t.id
                       LEFT JOIN rooms r ON g.room_id = r.id
                       ORDER BY g.id ASC""",
                    """SELECT g.id, g.name, p.name as program_name, t.name as tutor_name, r.name as room_name
                       FROM study_groups g
                       LEFT JOIN programs p ON g.program_id = p.id
                       LEFT JOIN tutors t ON g.tutor_id = t.id
                       LEFT JOIN rooms r ON g.room_id = r.id
                       ORDER BY g.id ASC"""
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/schedules':
                rows = db.query(
                    """SELECT sc.id, sc.day, sc.start_time, sc.end_time, g.name as group_name
                       FROM schedules sc
                       LEFT JOIN study_groups g ON sc.study_group_id = g.id
                       ORDER BY sc.id ASC""",
                    """SELECT sc.id, sc.day, sc.start_time, sc.end_time, g.name as group_name
                       FROM schedules sc
                       LEFT JOIN study_groups g ON sc.study_group_id = g.id
                       ORDER BY sc.id ASC"""
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/bills':
                rows = db.query(
                    """SELECT b.id, b.invoice_no, b.amount, b.due_date, b.status, s.name as student_name
                       FROM bills b
                       LEFT JOIN students s ON b.student_id = s.id
                       ORDER BY b.id DESC""",
                    """SELECT b.id, b.invoice_no, b.amount, b.due_date, b.status, s.name as student_name
                       FROM bills b
                       LEFT JOIN students s ON b.student_id = s.id
                       ORDER BY b.id DESC"""
                )
                self._send_json({"success": True, "data": rows})
                return

            elif path == '/api/payments':
                rows = db.query(
                    """SELECT p.id, p.receipt_no, p.amount, p.payment_date, p.payment_method, p.notes, b.invoice_no
                       FROM payments p
                       LEFT JOIN bills b ON p.bill_id = b.id
                       ORDER BY p.id DESC""",
                    """SELECT p.id, p.receipt_no, p.amount, p.payment_date, p.payment_method, p.notes, b.invoice_no
                       FROM payments p
                       LEFT JOIN bills b ON p.bill_id = b.id
                       ORDER BY p.id DESC"""
                )
                self._send_json({"success": True, "data": rows})
                return

            else:
                self._send_json({"error": "Endpoint tidak ditemukan"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._parse_body()

        try:
            # Konfigurasi Koneksi Neon PostgreSQL
            if path == '/api/config-db':
                neon_url = body.get('database_url', '').strip()
                if not neon_url:
                    self._send_json({"error": "DATABASE_URL tidak boleh kosong"}, 400)
                    return
                
                # Simpan ke file .env
                with open(ENV_FILE, 'w', encoding='utf-8') as f:
                    f.write(f"DATABASE_URL={neon_url}\nPORT={PORT}\n")
                
                os.environ['DATABASE_URL'] = neon_url
                db.db_url = neon_url
                success = db.check_connection()
                
                if success:
                    self._send_json({"success": True, "message": "Berhasil terhubung ke Neon PostgreSQL!", "database": "Neon PostgreSQL"})
                else:
                    self._send_json({"success": False, "message": f"Koneksi gagal: {db.last_error}. Berjalan dalam mode SQLite lokal."}, 400)
                return

            # Tambah Program Belajar
            elif path == '/api/programs':
                name = body.get('name', '').strip()
                level = body.get('level', 'SD').strip()
                sessions = int(body.get('sessions_per_month', 8))

                if not name:
                    self._send_json({"error": "Nama program wajib diisi"}, 400)
                    return

                new_id = db.execute_insert(
                    "INSERT INTO programs (name, level, sessions_per_month) VALUES (%s, %s, %s) RETURNING id",
                    "INSERT INTO programs (name, level, sessions_per_month) VALUES (?, ?, ?)",
                    (name, level, sessions)
                )

                self._send_json({
                    "success": True,
                    "message": "Program belajar berhasil ditambahkan",
                    "data": {"id": new_id, "name": name, "level": level, "sessions_per_month": sessions}
                }, 201)
                return

            # Tambah Siswa
            elif path == '/api/students':
                nis = body.get('nis', '').strip()
                name = body.get('name', '').strip()
                gender = body.get('gender', 'L').strip()
                guardian_name = body.get('guardian_name', '').strip()
                phone = body.get('phone', '').strip()
                program_id = body.get('program_id') or None
                status = body.get('status', 'Aktif')

                if not name or not guardian_name:
                    self._send_json({"error": "Nama siswa dan nama wali wajib diisi"}, 400)
                    return

                if not nis:
                    # Auto generate NIS
                    nis = f"OPT-{os.urandom(2).hex().upper()}"

                new_id = db.execute_insert(
                    "INSERT INTO students (nis, name, gender, guardian_name, phone, program_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    "INSERT INTO students (nis, name, gender, guardian_name, phone, program_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (nis, name, gender, guardian_name, phone, program_id, status)
                )

                self._send_json({"success": True, "message": "Data siswa berhasil ditambahkan", "id": new_id}, 201)
                return

            # Tambah Tutor
            elif path == '/api/tutors':
                name = body.get('name', '').strip()
                specialty = body.get('specialty', '').strip()
                phone = body.get('phone', '').strip()
                email = body.get('email', '').strip()
                status = body.get('status', 'Aktif')

                new_id = db.execute_insert(
                    "INSERT INTO tutors (name, specialty, phone, email, status) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    "INSERT INTO tutors (name, specialty, phone, email, status) VALUES (?, ?, ?, ?, ?)",
                    (name, specialty, phone, email, status)
                )
                self._send_json({"success": True, "message": "Data tutor berhasil disimpan", "id": new_id}, 201)
                return

            # Tambah Ruang
            elif path == '/api/rooms':
                name = body.get('name', '').strip()
                capacity = int(body.get('capacity', 10))
                facilities = body.get('facilities', '').strip()

                new_id = db.execute_insert(
                    "INSERT INTO rooms (name, capacity, facilities) VALUES (%s, %s, %s) RETURNING id",
                    "INSERT INTO rooms (name, capacity, facilities) VALUES (?, ?, ?)",
                    (name, capacity, facilities)
                )
                self._send_json({"success": True, "message": "Ruang belajar berhasil ditambahkan", "id": new_id}, 201)
                return

            else:
                self._send_json({"error": "Endpoint POST tidak ditemukan"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            parts = path.strip('/').split('/')
            if len(parts) == 3 and parts[0] == 'api':
                entity, entity_id = parts[1], parts[2]
                table_map = {
                    'programs': 'programs',
                    'students': 'students',
                    'tutors': 'tutors',
                    'rooms': 'rooms',
                    'groups': 'study_groups',
                    'schedules': 'schedules',
                    'bills': 'bills',
                    'payments': 'payments'
                }

                if entity in table_map:
                    table = table_map[entity]
                    db.query(
                        f"DELETE FROM {table} WHERE id = %s",
                        f"DELETE FROM {table} WHERE id = ?",
                        (int(entity_id),)
                    )
                    self._send_json({"success": True, "message": f"Data {entity} #{entity_id} berhasil dihapus"})
                    return

            self._send_json({"error": "Endpoint DELETE tidak ditemukan"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)


def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, AdminRequestHandler)
    print("="*60)
    print(f"🚀 Optimatika Admin Bimbel Backend berjalan di http://localhost:{PORT}")
    print(f"📦 Database Mode: {'Neon PostgreSQL' if db.use_postgres else 'SQLite Lokal'}")
    print("="*60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nMematikan server...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
