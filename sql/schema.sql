-- =======================================================
-- SCHEMA DATABASE BIMBEL OPTIMATIKA
-- Kompatibel dengan Neon PostgreSQL & SQLite
-- =======================================================

-- 1. TABEL PROGRAM BELAJAR (Sesuai Tampilan Utama)
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    level VARCHAR(20) NOT NULL, -- SD, SMP, SMA, UMUM
    sessions_per_month INTEGER NOT NULL DEFAULT 8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABEL TUTOR / PENGAJAR
CREATE TABLE IF NOT EXISTS tutors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABEL RUANG BELAJAR
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 10,
    facilities TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABEL SISWA DAN WALI
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    nis VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    gender VARCHAR(10) NOT NULL, -- L / P
    guardian_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'Aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABEL KELOMPOK BELAJAR (KELAS)
CREATE TABLE IF NOT EXISTS study_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    tutor_id INTEGER REFERENCES tutors(id) ON DELETE SET NULL,
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. TABEL JADWAL BELAJAR
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    study_group_id INTEGER REFERENCES study_groups(id) ON DELETE CASCADE,
    day VARCHAR(20) NOT NULL, -- Senin, Selasa, dst.
    start_time VARCHAR(10) NOT NULL, -- 15:30
    end_time VARCHAR(10) NOT NULL,   -- 17:00
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TABEL TAGIHAN SPP / BIAYA BIMBEL
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) UNIQUE NOT NULL,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Belum Lunas', -- Belum Lunas, Lunas, Dibatalkan
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. TABEL PEMBAYARAN
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    receipt_no VARCHAR(50) UNIQUE NOT NULL,
    bill_id INTEGER REFERENCES bills(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Transfer Bank', -- Transfer Bank, QRIS, Tunai
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. TABEL TUGAS SISWA & MODUL
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    tutor_id INTEGER REFERENCES tutors(id) ON DELETE SET NULL,
    due_date VARCHAR(50) NOT NULL,
    description TEXT,
    total_students INTEGER DEFAULT 0,
    submitted_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Berjalan', -- Berjalan, Selesai Dinilai, Perlu Koreksi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. TABEL ABSENSI / PRESENSI SISWA
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    schedule_id INTEGER REFERENCES schedules(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Hadir', -- Hadir, Sakit, Izin, Alpa
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================================================
-- DATA AWAL (SEED DATA PERSIS SEPERTI GAMBAR TAMPILAN)
-- =======================================================

INSERT INTO programs (name, level, sessions_per_month) VALUES 
('Calistung', 'SD', 8),
('Matematika SD', 'SD', 8),
('Matematika SMP', 'SMP', 8),
('IPA Terpadu', 'SMP', 8),
('Persiapan UTBK', 'SMA', 12)
ON CONFLICT DO NOTHING;

-- Data Awal Tutor
INSERT INTO tutors (name, specialty, phone, email, status) VALUES
('Kak Budi Santoso, S.Pd.', 'Matematika SD & SMP', '081234567890', 'budi@optimatika.id', 'Aktif'),
('Kak Siti Aminah, M.Si.', 'IPA Terpadu & Fisika', '081298765432', 'siti@optimatika.id', 'Aktif'),
('Kak Rizky Pratama, S.Si.', 'Matematika Saintek / UTBK', '085712345678', 'rizky@optimatika.id', 'Aktif')
ON CONFLICT DO NOTHING;

-- Data Awal Ruang Belajar
INSERT INTO rooms (name, capacity, facilities) VALUES
('Ruang Alpha (Lt. 1)', 8, 'AC, Smart Board, Dispenser'),
('Ruang Beta (Lt. 1)', 10, 'AC, Whiteboard, Modul Lengkap'),
('Ruang Gamma (Lt. 2)', 12, 'AC, Projector, Sound System')
ON CONFLICT DO NOTHING;

-- Data Awal Siswa
INSERT INTO students (nis, name, gender, guardian_name, phone, program_id, status) VALUES
('OPT-2026-001', 'Ahmad Farhan', 'L', 'Bpk. Hendra', '081211112222', 1, 'Aktif'),
('OPT-2026-002', 'Nabila Putri', 'P', 'Ibu Ratna', '081333334444', 2, 'Aktif'),
('OPT-2026-003', 'Dimas Anggara', 'L', 'Bpk. Bambang', '085655556666', 3, 'Aktif'),
('OPT-2026-004', 'Zahra Amelia', 'P', 'Ibu Dewi', '087777778888', 5, 'Aktif')
ON CONFLICT DO NOTHING;

-- Data Awal Tugas
INSERT INTO assignments (title, program_id, tutor_id, due_date, description, total_students, submitted_count, status) VALUES
('Latihan Aljabar & Persamaan Linear Bab 4', 3, 1, 'Hari Ini, 23:59', 'Kerjakan soal 1-15 pada modul halaman 42.', 10, 8, 'Berjalan'),
('Membaca Lancar Suku Kata & Angka', 1, 1, 'Besok, 17:00', 'Latihan dikte 5 kalimat dan penjumlahan puluhan.', 5, 5, 'Selesai Dinilai'),
('Simulasi Soal UTBK TPS Penalaran Matematika', 5, 3, '12 Nov 2026', 'Tryout online paket TPS 20 butir soal.', 4, 3, 'Perlu Koreksi'),
('Laporan Praktikum Sederhana Fluida Statis', 4, 2, '14 Nov 2026', 'Amati hukum Archimedes dengan air dan telur.', 6, 2, 'Berjalan')
ON CONFLICT DO NOTHING;
