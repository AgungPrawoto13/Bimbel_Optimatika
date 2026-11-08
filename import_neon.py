#!/usr/bin/env python3
"""
Script Helper untuk Import sql/schema.sql ke Neon PostgreSQL
Penggunaan:
    python3 import_neon.py
atau:
    python3 import_neon.py "postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require"
"""

import os
import sys

# Coba muat DATABASE_URL dari .env jika ada
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
db_url = ''
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                if k.strip() == 'DATABASE_URL':
                    db_url = v.strip().strip('"').strip("'")

# Jika diberikan via argumen command line
if len(sys.argv) > 1 and sys.argv[1].strip():
    db_url = sys.argv[1].strip()

# Jika masih kosong, minta input dari pengguna
if not db_url:
    print("=" * 60)
    print("  IMPORT SCHEMA SQL KE NEON POSTGRESQL (OPTIMATIKA)")
    print("=" * 60)
    print("Dapatkan string koneksi dari Neon Console (https://console.neon.tech)")
    print("Contoh: postgresql://alex:pass@ep-cool-12345.us-east-2.aws.neon.tech/neondb?sslmode=require\n")
    try:
        db_url = input("Masukkan Connection String Neon: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nDibatalkan.")
        sys.exit(0)

if not db_url:
    print("Error: Connection String tidak boleh kosong!")
    sys.exit(1)

# Cek apakah psycopg2 terpasang
try:
    import psycopg2
except ImportError:
    print("\n[!] Library 'psycopg2' belum terpasang.")
    print("Silakan pasang terlebih dahulu dengan perintah:")
    print("    pip install psycopg2-binary\n")
    sys.exit(1)

# Cari file schema.sql
schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql', 'schema.sql')
if not os.path.exists(schema_path):
    print(f"Error: File '{schema_path}' tidak ditemukan!")
    sys.exit(1)

print(f"\n[1/3] Membaca file {schema_path}...")
with open(schema_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("[2/3] Menghubungkan ke Neon PostgreSQL...")
try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    print("✓ Berhasil terhubung ke database Neon!")

    print("[3/3] Menjalankan perintah SQL (Membuat tabel & mengisi data awal)...")
    cur.execute(sql_script)
    conn.commit()

    # Hitung tabel yang terbuat
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    table_names = [t[0] for t in tables]

    cur.close()
    conn.close()

    # Simpan ke .env jika belum tersimpan
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write(f"DATABASE_URL={db_url}\nPORT=8000\n")

    print("\n" + "=" * 60)
    print("🎉 SUKSES! Database Neon PostgreSQL berhasil diimpor!")
    print("=" * 60)
    print("Daftar tabel yang aktif:")
    for name in table_names:
        print(f"  • {name}")
    print(f"\nKonfigurasi telah disimpan ke file .env.")
    print("Sekarang Anda bisa menjalankan 'python3 server.py' dalam mode Neon PostgreSQL!")

except Exception as e:
    print(f"\n[X] Terjadi kesalahan saat menghubungkan atau mengimpor:")
    print(f"    {e}")
    sys.exit(1)
