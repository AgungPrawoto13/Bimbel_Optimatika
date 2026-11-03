# Optimatika · Admin Bimbel

Aplikasi Web Panel Administrasi Bimbingan Belajar (Bimbel) **Optimatika**, dibangun menggunakan **HTML5, Bootstrap 5, Vanilla JavaScript**, dan backend yang siap dihubungkan langsung ke **Neon PostgreSQL** (cloud database gratis) atau **SQLite** lokal.

Desain antarmuka dibuat presisi mengikuti tampilan:
- Sidebar navigasi bernuansa *Deep Navy* dengan menu aktif bergaya *rounded pill*.
- Manajemen **Program Belajar** (Calistung, Matematika SD, Matematika SMP, IPA Terpadu, Persiapan UTBK) lengkap dengan input nama program, jenjang (SD/SMP/SMA), pertemuan per bulan, dan tombol hapus.
- Menu pelengkap operasional bimbel: **Siswa & Wali**, **Tutor**, **Ruang Belajar**, **Kelompok Belajar**, **Jadwal**, **Tagihan SPP**, dan **Pembayaran**.

---

## 📁 Struktur Direktori

```text
optimatika-admin/
├── public/
│   ├── css/
│   │   └── style.css          # Desain custom persis tampilan referensi
│   ├── js/
│   │   └── app.js             # Logika interaktif SPA & komunikasi REST API
│   └── index.html             # Tampilan utama web admin
├── sql/
│   └── schema.sql             # Skema tabel & data bawaan untuk PostgreSQL / SQLite
├── server.py                  # Backend server berbasis Python (Zero-dependency)
├── server.js                  # Backend server alternatif berbasis Node.js Express
├── package.json               # Konfigurasi package Node.js
├── requirements.txt           # Dependensi Python untuk koneksi langsung Neon
├── .env.example               # Contoh konfigurasi koneksi database
└── README.md                  # Dokumentasi panduan lengkap
```

---

## ⚡ Cara Menjalankan Aplikasi

Anda dapat memilih menjalankan backend menggunakan **Python** atau **Node.js**:

### Opsi A: Menggunakan Python (Sangat Mudah, Tanpa Install Tambahan)

Server Python sudah dilengkapi fallback SQLite otomatis, sehingga Anda bisa langsung menjalankannya:

1. Buka terminal di folder project:
   ```bash
   cd /home/ubuntu/.gemini/antigravity/scratch/optimatika-admin
   ```
2. Jalankan server:
   ```bash
   python3 server.py
   ```
3. Buka browser Anda di:
   ```text
   http://localhost:8000
   ```

*(Opsional: Jika ingin menghubungkan langsung ke Neon PostgreSQL lewat Python, instal driver `psycopg2`: `pip install -r requirements.txt`)*

---

### Opsi B: Menggunakan Node.js & Express

Jika Anda lebih terbiasa dengan ekosistem JavaScript/Node.js:

1. Masuk ke direktori project:
   ```bash
   cd /home/ubuntu/.gemini/antigravity/scratch/optimatika-admin
   ```
2. Pasang dependensi:
   ```bash
   npm install
   ```
3. Jalankan server:
   ```bash
   npm start
   ```
4. Buka di browser: `http://localhost:8000`

---

## 🐘 Panduan Menghubungkan ke Neon PostgreSQL (Gratis)

Neon (`neon.tech`) menyediakan database serverless PostgreSQL gratis dengan performa tinggi.

### 1. Dapatkan Connection String Neon
1. Buka dan login ke [Neon Console (https://console.neon.tech)](https://console.neon.tech).
2. Klik **Create Project** (misal beri nama `optimatika-bimbel`).
3. Pada halaman dashboard project, temukan bagian **Connection Details**.
4. Salin string koneksi **Postgres connection string**, contohnya:
   ```text
   postgresql://alex:AbC123dEf@ep-cool-fog-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### 2. Cara Menghubungkannya (Pilih salah satu):

#### Cara 1: Lewat Tampilan Web Admin (Paling Praktis)
1. Buka website di browser (`http://localhost:8000`).
2. Klik badge database di pojok kanan atas (ikon **⚙ Neon PostgreSQL**).
3. Tempelkan URL koneksi Neon yang sudah disalin ke dalam kolom yang tersedia.
4. Klik tombol **Simpan & Sambungkan**. Website akan otomatis menyimpan konfigurasi ke file `.env` dan menyambungkan data ke Neon!

#### Cara 2: Lewat File `.env`
1. Salin `.env.example` menjadi `.env` (atau edit file `.env` yang sudah ada):
   ```bash
   DATABASE_URL=postgresql://username:password@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   PORT=8000
   ```
2. Restart server (`python3 server.py` atau `npm start`).

### 3. Eksekusi Skema Tabel di Neon (Opsional)
Jika Anda ingin mengeksekusi tabel secara manual di dashboard Neon:
1. Buka menu **SQL Editor** di Neon Console.
2. Buka file `sql/schema.sql` di project ini, salin seluruh kodenya.
3. Tempel dan klik **Run**. Seluruh tabel dan data awal bimbel akan langsung terisi.

---

## 🎯 Fitur & Kemampuan

1. **Persis Seperti Gambar Referensi**:
   - Judul: *Data Program Belajar*
   - Subjudul: *Tarif tiap program ditetapkan pengelola di menu Tarif.*
   - Formulir *Tambah program* (Nama program, Jenjang dropdown, Pertemuan per bulan, Tombol Simpan).
   - Tabel responsif dengan badge jenjang (SD, SMP, SMA) dan tombol Hapus berdesain merah pill.
2. **Semua Menu Sidebar Aktif**:
   - **Siswa dan Wali**: Pendaftaran siswa baru, NIS otomatis, nama orang tua, dan tombol chat WhatsApp langsung.
   - **Tutor**: Manajemen nama pengajar, bidang keahlian, nomor telepon, dan status.
   - **Ruang Belajar**: Kapasitas siswa per kelas dan fasilitas (AC, Smart TV, dll).
   - **Kelompok Belajar, Jadwal, Tagihan & Pembayaran**: Manajemen operasional bimbel harian.
3. **Database Dual-Mode**:
   - Siap dipakai dengan Neon PostgreSQL via SSL.
   - Tetap dapat berjalan secara offline/lokal jika internet terputus atau sebelum akun Neon didaftarkan.
#Bimber Optimatika
