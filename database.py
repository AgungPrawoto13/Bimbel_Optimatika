import os
import sys
import time
import json
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
HTML_FILE = os.path.join(PUBLIC_DIR, 'program.html')


# =============================================================================
# 1. KONEKSI KE DATABASE NEON POSTGRESQL
# =============================================================================

def create_new_connection():
    """Membuka dan mengembalikan koneksi baru ke Neon PostgreSQL"""
    try:
        db_url = os.getenv("DATABASE_URL")
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
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, name, level, sessions_per_month FROM programs ORDER BY id ASC;")
            return cur.fetchall()
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
                  <button type="button" class="btn-delete-pill" onclick="hapusProgram(this, '{p_name}')">Hapus</button>
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
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": f"Program '{target}' dihapus"}).encode('utf-8'))
                return
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Nama program tidak ditemukan"}).encode('utf-8'))
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
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "id": new_id}).encode('utf-8'))
                return

        # 3. Default: sajikan file HTML/CSS/JS
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
        print(f"[{time.strftime('%H:%M:%S')}] ✓ Sinkronisasi awal sukses. Total: {total} program di database.")
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

            print("\n2. Melakukan sinkronisasi data ke public/program.html...")
            total = sync_ke_html()
            print(f"✓ Sukses! File public/program.html berhasil diisi dengan {total} program terbaru.")

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
