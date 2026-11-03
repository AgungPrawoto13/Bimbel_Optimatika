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
