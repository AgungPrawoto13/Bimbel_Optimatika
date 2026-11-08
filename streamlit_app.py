import os
import streamlit as st
import streamlit.components.v1 as components
import database

# =============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# =============================================================================
st.set_page_config(
    page_title="Optimatika · Data Program Belajar",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Menerapkan 100% Desain Asli Bimbel Optimatika
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        background-color: #f5f7fb !important;
    }

    /* ----------------- SIDEBAR DEEP NAVY ----------------- */
    section[data-testid="stSidebar"] {
        background-color: #131f38 !important;
        width: 260px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #8ea3c7 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Tombol Navigasi Sidebar */
    div[data-testid="stRadio"] > div {
        gap: 6px !important;
    }
    div[data-testid="stRadio"] label {
        padding: 8px 14px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }

    /* ----------------- CARDS & CONTAINERS ----------------- */
    .custom-card {
        background-color: #ffffff;
        border: 1px solid #f0f4f8;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02);
    }
    
    .card-heading {
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 18px;
    }
    
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #121826;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    
    .page-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 24px;
    }

    /* ----------------- BUTTONS ----------------- */
    /* Tombol Primary Biru (Simpan) */
    button[kind="primary"] {
        background-color: #1e50bb !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 44px !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #173fa0 !important;
        box-shadow: 0 4px 14px rgba(30, 80, 187, 0.28) !important;
    }

    /* Tombol Hapus (Outline Pill Merah persis desain asli) */
    button[kind="secondary"] {
        background: transparent !important;
        color: #dc2626 !important;
        border: 1px solid #fecaca !important;
        border-radius: 8px !important;
        padding: 4px 18px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        background-color: #fee2e2 !important;
        border-color: #f87171 !important;
    }

    /* Sembunyikan header/footer default Streamlit */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    footer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')


# =============================================================================
# 2. SIDEBAR DEEP NAVY (PERSIS SIDEBAR.JS ASLI)
# =============================================================================
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <div style="font-size: 20px; font-weight: 700; color: #ffffff;">
                Optimatika <span style="font-weight: 400; color: #8ea3c7;">· Admin</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Menu Navigasi",
        [
            "Dashboard",
            "Siswa dan Wali",
            "Program",
            "Tutor",
            "Ruang Belajar",
            "Kelompok Belajar",
            "Jadwal",
            "Tagihan",
            "Pembayaran"
        ],
        index=2,  # Default langsung ke menu 'Program'
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Status Koneksi Neon PostgreSQL
    try:
        conn = database.create_new_connection()
        conn.close()
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; font-size: 13px; color: #22c55e;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #22c55e; display: inline-block;"></span>
                <span>Neon PostgreSQL Terhubung</span>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"<span style='color: #ef4444; font-size: 12px;'>✗ Offline: {e}</span>", unsafe_allow_html=True)


# =============================================================================
# 3. KONTEN UTAMA: HALAMAN PROGRAM BELAJAR
# =============================================================================
if menu == "Program":
    # TOP HEADER
    st.markdown("<h1 class='page-title'>Data Program Belajar</h1>", unsafe_allow_html=True)
    st.markdown("<p class='page-subtitle'>Daftar program bimbingan belajar yang terdaftar di database Neon PostgreSQL.</p>", unsafe_allow_html=True)

    # CARD 1: FORM TAMBAH PROGRAM (AKTIF & LANGSUNG AUTO-REFRESH)
    st.markdown('<div class="custom-card"><div class="card-heading">Tambah program</div>', unsafe_allow_html=True)
    with st.form("form_add_program", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            nama_input = st.text_input("Nama program", placeholder="contoh: Matematika Dasar")
        with col2:
            jenjang_input = st.selectbox("Jenjang", ["SD", "SMP", "SMA"])
        with col3:
            sesi_input = st.number_input("Pertemuan per bulan", min_value=1, max_value=31, value=8)
        with col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_simpan = st.form_submit_button("Simpan", type="primary", use_container_width=True)

        if btn_simpan and nama_input.strip():
            try:
                new_id = database.add_program(nama_input.strip(), jenjang_input, sesi_input)
                # Auto-sync ke file HTML lokal
                try:
                    database.sync_ke_html()
                except Exception:
                    pass
                st.toast(f"✓ Program '{nama_input}' berhasil ditambahkan ke Neon!", icon="🎉")
                st.rerun()  # Auto-refresh instan tanpa perlu reload manual
            except Exception as e:
                st.error(f"Gagal menambahkan program: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # CARD 2: TABEL DATA PROGRAM DARI NEON POSTGRESQL (TAMPIL & HAPUS AKTIF)
    st.markdown("""
        <div class="custom-card" style="padding: 0; overflow: hidden;">
    """, unsafe_allow_html=True)

    # Header Tabel
    th1, th2, th3, th4 = st.columns([4, 2, 2, 2])
    with th1:
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #8292a8; letter-spacing: 0.6px; padding: 14px 20px 8px 20px;'>PROGRAM</div>", unsafe_allow_html=True)
    with th2:
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #8292a8; letter-spacing: 0.6px; padding: 14px 0 8px 0;'>JENJANG</div>", unsafe_allow_html=True)
    with th3:
        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #8292a8; letter-spacing: 0.6px; padding: 14px 0 8px 0;'>PERTEMUAN / BULAN</div>", unsafe_allow_html=True)
    with th4:
        st.markdown("<div style='padding: 14px 20px 8px 0;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='border-bottom: 1.5px solid #edf2f7;'></div>", unsafe_allow_html=True)

    # Baris Data Program
    try:
        programs = database.get_programs()
        if not programs:
            st.markdown("<p style='text-align: center; color: #64748b; padding: 30px 0;'>Belum ada data program di database Neon.</p>", unsafe_allow_html=True)
        else:
            for p in programs:
                r1, r2, r3, r4 = st.columns([4, 2, 2, 2])
                with r1:
                    st.markdown(f"<div style='font-size: 14.5px; font-weight: 600; color: #1e293b; padding: 12px 20px 0 20px;'>{p['name']}</div>", unsafe_allow_html=True)
                with r2:
                    lvl = str(p['level']).upper()
                    if lvl == "SMP":
                        bg, col = "#ebf4ff", "#3182ce"
                    elif lvl == "SMA":
                        bg, col = "#e6f6ff", "#0284c7"
                    else:
                        bg, col = "#e6f0ff", "#2b6cb0"
                    st.markdown(f"<div style='padding-top: 10px;'><span style='background-color: {bg}; color: {col}; font-weight: 700; font-size: 12px; padding: 4px 14px; border-radius: 9999px;'>{lvl}</span></div>", unsafe_allow_html=True)
                with r3:
                    st.markdown(f"<div style='font-size: 14px; color: #334155; font-weight: 500; padding-top: 12px;'>{p['sessions_per_month']}×</div>", unsafe_allow_html=True)
                with r4:
                    st.markdown("<div style='text-align: right; padding: 6px 20px 0 0;'>", unsafe_allow_html=True)
                    if st.button("Hapus", key=f"btn_del_{p['id']}", type="secondary"):
                        try:
                            database.delete_program(p['id'])
                            # Sync ke program.html lokal
                            try:
                                database.sync_ke_html()
                            except Exception:
                                pass
                            st.toast(f"✓ Program '{p['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                            st.rerun()  # Auto-refresh instan tanpa perlu reload manual
                        except Exception as e:
                            st.error(f"Gagal menghapus: {e}")
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div style='border-bottom: 1px solid #f1f5f9;'></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal mengambil data dari database Neon: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 4. MENU LAINNYA: TAMPILKAN FILE HTML DARI FOLDER PUBLIC/
# =============================================================================
else:
    file_map = {
        "Dashboard": "dashboard.html",
        "Siswa dan Wali": "siswa.html",
        "Tutor": "tutor.html",
        "Ruang Belajar": "ruang_belajar.html",
        "Kelompok Belajar": "kelompok_belajar.html",
        "Jadwal": "jadwal.html",
        "Tagihan": "tagihan.html",
        "Pembayaran": "pembayaran.html"
    }

    target_file = file_map.get(menu, "dashboard.html")
    file_path = os.path.join(PUBLIC_DIR, target_file)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        # Sisipkan CSS & JS asli
        css_path = os.path.join(PUBLIC_DIR, 'css', 'style.css')
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as cf:
                raw_html = raw_html.replace('<link rel="stylesheet" href="css/style.css">', f'<style>\n{cf.read()}\n</style>')

        components.html(raw_html, height=1100, scrolling=True)
    else:
        st.warning(f"File {target_file} belum ditemukan di folder public/.")
