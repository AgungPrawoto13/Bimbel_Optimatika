import os
import sys
import time
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'public', 'program.html')


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


def delete_program(program_id):
    """Menghapus program berdasarkan ID dari database Neon PostgreSQL"""
    conn = create_new_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM programs WHERE id = %s;", (program_id,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


# =============================================================================
# 3. FUNGSI SINKRONISASI OTOMATIS KE FILE HTML (TANPA PERLU SERVER)
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

            row = f"""              <tr>
                <td><strong>{p['name']}</strong></td>
                <td><span class="{badge_class}">{level}</span></td>
                <td><span class="session-count">{p['sessions_per_month']}×</span></td>
                <td class="text-end pe-4 text-muted" style="font-size: 13px;">
                  <span class="badge bg-light text-secondary border">ID: {p['id']}</span>
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
# 4. MODE STANDBY / SIAGA DI BACKGROUND (AUTO-SYNC REALTIME)
# =============================================================================

def start_standby_mode(interval=3):
    """
    Menjalankan database.py dalam mode STANDBY / SIAGA.
    Secara berkala mengecek database Neon PostgreSQL setiap 'interval' detik.
    Jika ada penambahan, perubahan, atau penghapusan program di Neon,
    langsung otomatis mengupdate public/program.html!
    """
    print("\n" + "=" * 60)
    print("   [STANDBY MODE] DATABASE.PY AKTIF & SIAGA DI BACKGROUND")
    print("=" * 60)
    print(f"✓ Status: STANDBY (Terus berjalan)")
    print(f"✓ Interval pengecekan: Setiap {interval} detik ke Neon PostgreSQL")
    print("✓ Deteksi otomatis: Jika data di Neon berubah, program.html langsung auto-update")
    print("✓ Tekan [CTRL + C] di terminal kapan pun jika ingin berhenti.\n")

    # Sinkronisasi awal
    last_state = None
    try:
        total = sync_ke_html()
        programs = get_programs()
        last_state = [(p['id'], p['name'], p['level'], p['sessions_per_month']) for p in programs]
        print(f"[{time.strftime('%H:%M:%S')}] ✓ Sinkronisasi awal sukses. Total: {total} program di database.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ! Gagal sinkronisasi awal: {e}")

    # Loop standby di background
    try:
        while True:
            time.sleep(interval)
            try:
                programs = get_programs()
                current_state = [(p['id'], p['name'], p['level'], p['sessions_per_month']) for p in programs]

                # Jika ada perubahan (tambah, edit, atau hapus) di Neon
                if current_state != last_state:
                    total = sync_ke_html()
                    last_state = current_state
                    print(f"[{time.strftime('%H:%M:%S')}] 🔔 Perubahan data terdeteksi di Neon! Auto-update program.html berhasil (Total: {total} program).")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] ! Peringatan koneksi: {e}")
                time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n✓ Mode standby dihentikan. database.py selesai.")


# =============================================================================
# 5. RUNNER CLI INTERAKTIF (python database.py)
# =============================================================================
if __name__ == '__main__':
    args = sys.argv[1:]

    # OPSI 1: MODE STANDBY -> python database.py standby (atau watch / monitor)
    if len(args) >= 1 and args[0].lower() in ['standby', 'watch', 'monitor', 'live']:
        start_standby_mode(interval=3)

    # OPSI 2: Hapus data lewat terminal -> python database.py hapus <id>
    elif len(args) >= 2 and args[0].lower() in ['hapus', 'delete']:
        prog_id = int(args[1])
        print(f"\nMenghapus program ID {prog_id} dari database Neon...")
        if delete_program(prog_id):
            print(f"✓ Berhasil menghapus program ID {prog_id} dari database Neon.")
        else:
            print(f"! Program ID {prog_id} tidak ditemukan di database.")
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
            print(" • Agar selalu STANDBY di background : python database.py standby")
            print(" • Tambah program                    : python database.py tambah \"Nama Program\" Jenjang Pertemuan")
            print(" • Hapus program                     : python database.py hapus <ID>")
            print("=" * 60)

        except Exception as e:
            print(f"\n✗ Terjadi kendala: {e}")
