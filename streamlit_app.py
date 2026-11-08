import os
import streamlit as st
import streamlit.components.v1 as components
import database

# =============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# =============================================================================
st.set_page_config(
    page_title="Optimatika · Admin Bimbel",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hilangkan margin berlebih Streamlit agar tampilan HTML di folder public/ tampil penuh
st.markdown("""
<style>
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
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
# 2. FUNGSI PENGGABUNG FILE HTML DENGAN CSS & JS DARI FOLDER PUBLIC
# =============================================================================

def get_bundled_html(filename):
    """
    Membaca file HTML dari folder public/ dan menyematkan langsung:
    1. Sinkronisasi data live dari Neon PostgreSQL (jika program.html)
    2. File css/style.css
    3. File js/sidebar.js dengan navigasi otomatis antar halaman
    """
    filepath = os.path.join(PUBLIC_DIR, filename)
    if not os.path.exists(filepath):
        return f"<h3>File '{filename}' tidak ditemukan di folder public/.</h3>"

    # 1. Auto-sync data terbaru dari Neon PostgreSQL ke program.html
    if filename == "program.html":
        try:
            database.sync_ke_html()
        except Exception:
            pass

    # 2. Baca file HTML asli
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 3. Gabungkan file public/css/style.css langsung ke dalam tag <style>
    css_path = os.path.join(PUBLIC_DIR, 'css', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as cf:
            css_code = cf.read()
        html = html.replace(
            '<link rel="stylesheet" href="css/style.css">',
            f'<style>\n{css_code}\n</style>'
        )

    # 4. Gabungkan file public/js/sidebar.js dan sesuaikan link navigasi
    js_path = os.path.join(PUBLIC_DIR, 'js', 'sidebar.js')
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as jf:
            js_code = jf.read()

        # Ubah link menu di sidebar.js agar saat diklik di browser langsung berpindah halaman di Streamlit
        js_code = js_code.replace(
            'href="${item.link}"',
            'href="javascript:void(0)" onclick="window.top.location.search = \'?page=\' + encodeURIComponent(\'${item.link}\');"'
        )

        html = html.replace(
            '<script src="js/sidebar.js"></script>',
            f'<script>\n{js_code}\n</script>'
        )

    return html


# =============================================================================
# 3. SIDEBAR: PENGATURAN & NAVIGASI FOLDER PUBLIC
# =============================================================================

# Ambil halaman aktif dari URL query parameter (misal: ?page=dashboard.html)
url_page = st.query_params.get("page", "program.html")

file_options = [
    ("program.html", "📚 Data Program Belajar (program.html)"),
    ("dashboard.html", "📊 Dashboard (dashboard.html)"),
    ("siswa.html", "👨‍🎓 Data Siswa dan Wali (siswa.html)"),
    ("tutor.html", "👨‍🏫 Data Tutor (tutor.html)"),
    ("jadwal.html", "📅 Jadwal Belajar (jadwal.html)"),
    ("tagihan.html", "🧾 Tagihan SPP (tagihan.html)"),
    ("pembayaran.html", "💳 Pembayaran (pembayaran.html)"),
    ("ruang_belajar.html", "🏢 Ruang Belajar (ruang_belajar.html)"),
    ("kelompok_belajar.html", "👥 Kelompok Belajar (kelompok_belajar.html)"),
    ("index.html", "🔐 Halaman Login (index.html)")
]

file_keys = [opt[0] for opt in file_options]
default_index = file_keys.index(url_page) if url_page in file_keys else 0

with st.sidebar:
    st.markdown("## **Optimatika** `· Admin`")
    st.caption("Fokus: Memuat Langsung File HTML di Folder `public/`")
    st.divider()

    selected_label = st.radio(
        "Buka Halaman HTML di public/:",
        options=[opt[1] for opt in file_options],
        index=default_index
    )
    # Temukan nama file yang dipilih
    selected_file = [opt[0] for opt in file_options if opt[1] == selected_label][0]

    st.divider()

    # Form cepat untuk tambah program langsung ke Neon dari sidebar
    with st.expander("➕ Tambah Program Baru ke Neon"):
        with st.form("sidebar_add_prog", clear_on_submit=True):
            p_name = st.text_input("Nama Program", placeholder="Misal: Fisika SMA")
            p_level = st.selectbox("Jenjang", ["SD", "SMP", "SMA"])
            p_sessions = st.number_input("Sesi / Bulan", min_value=1, max_value=31, value=8)
            btn_add = st.form_submit_button("Simpan ke Neon")
            if btn_add and p_name.strip():
                try:
                    new_id = database.add_program(p_name.strip(), p_level, p_sessions)
                    database.sync_ke_html()
                    st.success(f"✓ Berhasil tambah {p_name}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # Form cepat untuk hapus program dari Neon
    with st.expander("🗑️ Hapus Program dari Neon"):
        try:
            curr_progs = database.get_programs()
            if curr_progs:
                prog_to_del = st.selectbox(
                    "Pilih program yang ingin dihapus:",
                    options=[f"{p['id']} - {p['name']}" for p in curr_progs]
                )
                if st.button("Hapus Program Ini", type="primary"):
                    del_id = int(prog_to_del.split(" - ")[0])
                    database.delete_program(del_id)
                    database.sync_ke_html()
                    st.success("✓ Program berhasil dihapus!")
                    st.rerun()
            else:
                st.caption("Tidak ada program di database.")
        except Exception:
            pass

    st.divider()
    st.markdown("### ⚡ Status Neon Database")
    try:
        conn = database.create_new_connection()
        conn.close()
        st.success("✓ Neon PostgreSQL: Terhubung")
    except Exception as e:
        st.error(f"✗ Gagal: {e}")


# =============================================================================
# 4. KONTEN UTAMA: RENDER 100% FILE HTML DARI FOLDER PUBLIC/
# =============================================================================

# Render file HTML asli dari folder public/ lengkap dengan CSS & Sidebar
rendered_html = get_bundled_html(selected_file)
components.html(rendered_html, height=1100, scrolling=True)
