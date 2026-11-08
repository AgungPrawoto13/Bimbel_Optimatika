import os
import streamlit as st
import streamlit.components.v1 as components
import database

# =============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# =============================================================================
st.set_page_config(
    page_title="Optimatika · Admin Bimbel",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling agar senada dengan desain antarmuka Bimbel Optimatika
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Brand */
    .brand-title {
        font-size: 24px;
        font-weight: 700;
        color: #131f38;
        margin-bottom: 4px;
    }
    .brand-sub {
        color: #64748b;
        font-weight: 400;
    }
    
    /* Card Container */
    .stCard {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Badges */
    .badge-sd {
        background-color: #e6f0ff;
        color: #1e50bb;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-smp {
        background-color: #f0fdf4;
        color: #16a34a;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-sma {
        background-color: #fef3c7;
        color: #d97706;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
with st.sidebar:
    st.markdown("## **Optimatika** `· Admin`")
    st.caption("Sistem Manajemen Bimbingan Belajar")
    st.divider()

    menu = st.radio(
        "Pilih Menu Navigasi:",
        [
            "📊 Dashboard",
            "📚 Data Program Belajar",
            "🌐 Preview Halaman HTML Asli",
            "ℹ️ Status Database Neon"
        ],
        index=1  # Default langsung ke Data Program Belajar
    )

    st.divider()
    st.markdown("### ⚡ Info Database")
    try:
        conn = database.create_new_connection()
        conn.close()
        st.success("✓ Neon PostgreSQL: Terhubung")
    except Exception as e:
        st.error(f"✗ Database Offline: {e}")


# =============================================================================
# 1. MENU: DATA PROGRAM BELAJAR
# =============================================================================
if menu == "📚 Data Program Belajar":
    st.markdown("<h1 class='brand-title'>Data Program Belajar</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-sub'>Daftar program bimbingan belajar yang tersimpan di Neon PostgreSQL.</p>", unsafe_allow_html=True)

    # CARD: FORM TAMBAH PROGRAM
    with st.expander("➕ Tambah Program Belajar Baru", expanded=True):
        with st.form("form_tambah_program", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                nama_prog = st.text_input("Nama Program", placeholder="contoh: Fisika Dasar")
            with col2:
                jenjang_prog = st.selectbox("Jenjang", ["SD", "SMP", "SMA"])
            with col3:
                sesi_prog = st.number_input("Pertemuan / Bulan", min_value=1, max_value=31, value=8)

            submitted = st.form_submit_button("Simpan Program ke Database")
            if submitted:
                if not nama_prog.strip():
                    st.warning("Nama program tidak boleh kosong!")
                else:
                    try:
                        new_id = database.add_program(nama_prog.strip(), jenjang_prog, sesi_prog)
                        # Sinkronisasi juga ke file program.html lokal jika ada
                        try:
                            database.sync_ke_html()
                        except Exception:
                            pass
                        st.success(f"✓ Program '{nama_prog}' berhasil ditambahkan ke Neon! (ID: {new_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan program: {e}")

    st.divider()

    # CARD: TABEL DAFTAR PROGRAM DARI NEON
    st.markdown("### 📋 Daftar Program Aktif")

    try:
        programs = database.get_programs()
        if not programs:
            st.info("Belum ada data program di database Neon PostgreSQL.")
        else:
            # Header Tabel
            col_h1, col_h2, col_h3, col_h4 = st.columns([4, 2, 2, 2])
            with col_h1:
                st.markdown("**PROGRAM**")
            with col_h2:
                st.markdown("**JENJANG**")
            with col_h3:
                st.markdown("**PERTEMUAN / BULAN**")
            with col_h4:
                st.markdown("<div style='text-align: right;'>**AKSI**</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

            # Baris Data Program
            for p in programs:
                col_d1, col_d2, col_d3, col_d4 = st.columns([4, 2, 2, 2])
                with col_d1:
                    st.markdown(f"**{p['name']}**")
                with col_d2:
                    lvl = str(p['level']).upper()
                    badge_class = "badge-sd" if lvl == "SD" else ("badge-smp" if lvl == "SMP" else "badge-sma")
                    st.markdown(f"<span class='{badge_class}'>{lvl}</span>", unsafe_allow_html=True)
                with col_d3:
                    st.markdown(f"{p['sessions_per_month']}× / bulan")
                with col_d4:
                    # Tombol Hapus per Baris
                    if st.button("Hapus", key=f"btn_del_{p['id']}", help=f"Hapus {p['name']} dari database"):
                        try:
                            database.delete_program(p['id'])
                            # Sync ke program.html
                            try:
                                database.sync_ke_html()
                            except Exception:
                                pass
                            st.toast(f"Program '{p['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menghapus program: {e}")

                st.markdown("<hr style='margin: 4px 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca data program: {e}")


# =============================================================================
# 2. MENU: DASHBOARD
# =============================================================================
elif menu == "📊 Dashboard":
    st.markdown("<h1 class='brand-title'>Dashboard Operasional</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-sub'>Ringkasan performa dan data bimbingan belajar Optimatika.</p>", unsafe_allow_html=True)

    try:
        programs = database.get_programs()
        total_programs = len(programs)
    except Exception:
        total_programs = 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Program Belajar", value=f"{total_programs} Program")
    with col2:
        st.metric(label="Status Server", value="Online")
    with col3:
        st.metric(label="Database", value="Neon Cloud")
    with col4:
        st.metric(label="SSL Encrypted", value="Aktif")

    st.divider()
    st.markdown("### 📌 Fitur Unggulan")
    st.info("Aplikasi ini berjalan di atas Streamlit Cloud dan terhubung langsung secara realtime dengan Neon PostgreSQL.")


# =============================================================================
# 3. MENU: PREVIEW HALAMAN HTML ASLI
# =============================================================================
elif menu == "🌐 Preview Halaman HTML Asli":
    st.markdown("<h1 class='brand-title'>Preview Source Code HTML Asli</h1>", unsafe_allow_html=True)
    st.markdown("<p class='brand-sub'>Seluruh file HTML dan CSS asli dalam project tetap dipertahankan 100%.</p>", unsafe_allow_html=True)

    pilihan_file = st.selectbox(
        "Pilih file HTML yang ingin ditampilkan:",
        [
            "program.html",
            "dashboard.html",
            "siswa.html",
            "tutor.html",
            "jadwal.html",
            "tagihan.html",
            "pembayaran.html",
            "ruang_belajar.html",
            "kelompok_belajar.html",
            "index.html"
        ]
    )

    file_path = os.path.join(PUBLIC_DIR, pilihan_file)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            html_raw = f.read()

        tab1, tab2 = st.tabs(["👁️ Tampilan Visual (Iframe)", "📄 Source Code HTML"])
        with tab1:
            components.html(html_raw, height=750, scrolling=True)
        with tab2:
            st.code(html_raw, language="html")
    else:
        st.warning(f"File {pilihan_file} tidak ditemukan di folder public/.")


# =============================================================================
# 4. MENU: STATUS DATABASE NEON
# =============================================================================
elif menu == "ℹ️ Status Database Neon":
    st.markdown("<h1 class='brand-title'>Status Koneksi Neon PostgreSQL</h1>", unsafe_allow_html=True)
    try:
        conn = database.create_new_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            ver = cur.fetchone()[0]
        conn.close()

        st.success("✓ Berhasil terhubung ke Neon PostgreSQL!")
        st.code(ver, language="text")
        st.markdown("**Konfigurasi Rahasia (Secrets):**")
        st.caption("Saat di-deploy ke Streamlit Community Cloud, masukkan `DATABASE_URL` ke bagian Settings -> Secrets.")
    except Exception as e:
        st.error(f"✗ Gagal terhubung ke database: {e}")
