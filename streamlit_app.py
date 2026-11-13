import html
import importlib
import os
import textwrap
import streamlit as st
import streamlit.components.v1 as components
import database 

# Pastikan modul database ikut ter-reload saat file database.py berubah (anti-cache di Streamlit Cloud)
_db_file = getattr(database, "__file__", None)
if _db_file and os.path.exists(_db_file):
    _db_mtime = os.path.getmtime(_db_file)
    if st.session_state.get("_db_mtime") != _db_mtime or not hasattr(database, "get_tutors") or not hasattr(database, "get_students") or not hasattr(database, "get_billing_summary") or not hasattr(database, "publish_bills_for_period"):
        importlib.reload(database)
        st.session_state["_db_mtime"] = _db_mtime

# =============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# =============================================================================
st.set_page_config(
    page_title="Optimatika · Bimbel Admin",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Presisi 100% sesuai public/program.html & public/css/style.css
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --sidebar-bg: #131f38;
        --sidebar-hover: rgba(255, 255, 255, 0.08);
        --sidebar-text: #8ea3c7;
        --sidebar-active-bg: #ffffff;
        --sidebar-active-text: #131f38;
        --primary-blue: #1e50bb;
        --primary-hover: #173fa0;
        --bg-main: #f5f7fb;
        --card-bg: #ffffff;
        --card-border: #f0f4f8;
        --text-dark: #121826;
        --text-muted: #64748b;
        --text-table-head: #8292a8;
        --danger-border: #fecaca;
        --danger-text: #dc2626;
        --danger-bg-hover: #fee2e2;
    }

    html, body, [class*="css"], .stApp, button, input, select, textarea {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    section[data-testid="stMain"] {
        background-color: var(--bg-main) !important;
        color: var(--text-dark) !important;
    }

    /* Sembunyikan chrome bawaan Streamlit agar bersih seperti halaman web asli */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }
    #MainMenu,
    footer,
    [data-testid="stDecoration"],
    [data-testid="stToolbarActions"],
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Padding area konten utama persis .main-wrapper (36px 44px) */
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding: 36px 44px 48px 44px !important;
        max-width: 100% !important;
    }

    /* ----------------- SIDEBAR DEEP NAVY (260px) ----------------- */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        border-right: none !important;
    }

    @media (min-width: 992px) {
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding: 24px 16px !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
    }

    .brand-container {
        padding: 8px 12px 26px 12px;
    }

    .brand-title {
        font-size: 19px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.2px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .brand-sub {
        font-weight: 400;
        color: var(--sidebar-text);
    }

    /* Tombol Menu Sidebar tanpa radio dot */
    section[data-testid="stSidebar"] div[data-testid="stButton"] {
        margin: 0 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button > div,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stMarkdownContainer"] p {
        width: auto !important;
        flex: 0 1 auto !important;
        text-align: left !important;
        justify-content: flex-start !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    section[data-testid="stSidebar"] button[kind="secondary"],
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"],
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: var(--sidebar-text) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        min-height: 0 !important;
        height: auto !important;
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] button[kind="secondary"] p,
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] p,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] p {
        color: var(--sidebar-text) !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    section[data-testid="stSidebar"] button[kind="secondary"]:hover,
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
        background-color: var(--sidebar-hover) !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] button[kind="secondary"]:hover p,
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover p,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover p {
        color: #ffffff !important;
    }

    /* Menu Aktif (Pill Putih) */
    section[data-testid="stSidebar"] button[kind="primary"],
    section[data-testid="stSidebar"] button[data-testid="baseButton-primary"],
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
        background-color: var(--sidebar-active-bg) !important;
        color: var(--sidebar-active-text) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        min-height: 0 !important;
        height: auto !important;
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] button[kind="primary"] p,
    section[data-testid="stSidebar"] button[data-testid="baseButton-primary"] p,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p {
        color: var(--sidebar-active-text) !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    /* Footer Keluar di bagian paling bawah sidebar */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider),
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) {
        margin-top: auto !important;
        padding-top: 16px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    .sidebar-footer-divider {
        height: 0;
        margin: 0;
        padding: 0;
    }

    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider) + [data-testid="stElementContainer"] button,
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) + [data-testid="element-container"] button {
        padding: 8px 12px !important;
        border-radius: 8px !important;
        gap: 10px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider) + [data-testid="stElementContainer"] button p,
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) + [data-testid="element-container"] button p {
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider) + [data-testid="stElementContainer"] button::before,
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) + [data-testid="element-container"] button::before {
        content: "";
        display: inline-block;
        width: 15px;
        height: 15px;
        flex-shrink: 0;
        background-color: currentColor;
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M6 12.5a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v2a.5.5 0 0 1-1 0v-2A1.5 1.5 0 0 1 6.5 2h8A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 5 12.5v-2a.5.5 0 0 1 1 0z'/%3E%3Cpath fill-rule='evenodd' d='M.146 8.354a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L1.707 7.5H10.5a.5.5 0 0 1 0 1H1.707l2.147 2.146a.5.5 0 0 1-.708.708z'/%3E%3C/svg%3E") no-repeat center / contain;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M6 12.5a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v2a.5.5 0 0 1-1 0v-2A1.5 1.5 0 0 1 6.5 2h8A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 5 12.5v-2a.5.5 0 0 1 1 0z'/%3E%3Cpath fill-rule='evenodd' d='M.146 8.354a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L1.707 7.5H10.5a.5.5 0 0 1 0 1H1.707l2.147 2.146a.5.5 0 0 1-.708.708z'/%3E%3C/svg%3E") no-repeat center / contain;
    }

    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider) + [data-testid="stElementContainer"] button:hover,
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) + [data-testid="element-container"] button:hover {
        color: #f87171 !important;
        background-color: rgba(239, 68, 68, 0.1) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer-divider) + [data-testid="stElementContainer"] button:hover p,
    section[data-testid="stSidebar"] [data-testid="element-container"]:has(.sidebar-footer-divider) + [data-testid="element-container"] button:hover p {
        color: #f87171 !important;
    }

    /* ----------------- TOP HEADER ----------------- */
    .page-title {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--text-dark) !important;
        letter-spacing: -0.5px !important;
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
        line-height: 1.25 !important;
    }

    .page-subtitle {
        color: var(--text-muted) !important;
        font-size: 14px !important;
        margin: 0 0 24px 0 !important;
        padding: 0 !important;
        line-height: 1.5 !important;
    }

    /* ----------------- CARD 1: FORM TAMBAH PROGRAM ----------------- */
    div[data-testid="stForm"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
    }

    div[data-testid="stForm"] [data-testid="stVerticalBlock"] {
        gap: 0.75rem !important;
    }

    .card-heading {
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 10px 0;
        line-height: 1.4;
    }

    /* Label input */
    div[data-testid="stForm"] [data-testid="stWidgetLabel"] {
        min-height: 20px !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stForm"] [data-testid="stWidgetLabel"] p {
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        margin: 0 !important;
    }

    /* Sembunyikan hint "Press Enter to submit form" */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Text & Number Input putih bersih dengan border #e2e8f0 */
    div[data-testid="stForm"] div[data-testid="stTextInputRootElement"],
    div[data-testid="stForm"] div[data-testid="stNumberInputContainer"],
    div[data-testid="stForm"] div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        height: 44px !important;
        min-height: 44px !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
    }

    div[data-testid="stForm"] div[data-testid="stTextInputRootElement"] div[data-baseweb="input"],
    div[data-testid="stForm"] div[data-testid="stNumberInputContainer"] div[data-baseweb="input"] {
        border: none !important;
        height: 41px !important;
        min-height: 41px !important;
    }

    div[data-testid="stForm"] div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stForm"] div[data-testid="stNumberInputContainer"]:focus-within,
    div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    div[data-testid="stForm"] div[data-testid="stTextInputRootElement"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stForm"] div[data-testid="stNumberInputContainer"] div[data-baseweb="input"]:focus-within {
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border: none !important;
    }

    div[data-testid="stForm"] div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-size: 14.5px !important;
        padding: 8px 14px !important;
        height: 41px !important;
        -webkit-text-fill-color: #1e293b !important;
    }

    div[data-testid="stForm"] div[data-baseweb="input"] input::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }

    /* Sembunyikan tombol stepper - / + pada number input agar sama dengan HTML input */
    div[data-testid="stForm"] div[data-testid="stNumberInput"] button {
        display: none !important;
    }

    /* Selectbox Jenjang */
    div[data-testid="stForm"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        height: 44px !important;
        min-height: 44px !important;
        padding-left: 8px !important;
        font-size: 14.5px !important;
        color: #1e293b !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] div[data-baseweb="select"] > div:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    /* Tombol Simpan (Biru #1e50bb sejajar di bawah input seperti .align-items-end) */
    div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
    }

    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] {
        margin-top: 0 !important;
    }

    div[data-testid="stFormSubmitButton"] button,
    button[kind="primaryFormSubmit"],
    button[data-testid="baseButton-primaryFormSubmit"],
    button[data-testid="stBaseButton-primaryFormSubmit"] {
        background-color: var(--primary-blue) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        height: 44px !important;
        min-height: 44px !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stFormSubmitButton"] button p,
    button[kind="primaryFormSubmit"] p,
    button[data-testid="baseButton-primaryFormSubmit"] p,
    button[data-testid="stBaseButton-primaryFormSubmit"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        margin: 0 !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid="baseButton-primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background-color: var(--primary-hover) !important;
        box-shadow: 0 4px 14px rgba(30, 80, 187, 0.28) !important;
    }

    /* ----------------- CARD 2: TABEL DATA PROGRAM ----------------- */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .table-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .table-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .table-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="element-container"] .table-card-marker) {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 0 !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
        margin-bottom: 24px !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) {
        gap: 0 !important;
        padding: 0 !important;
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) {
        border: none !important;
        box-shadow: none !important;
    }

    [data-testid="stElementContainer"]:has(.table-card-marker),
    [data-testid="element-container"]:has(.table-card-marker) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Baris Header & Data di dalam Tabel Card */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="stHorizontalBlock"] {
        padding: 14px 24px 14px 20px !important;
        margin: 0 !important;
        align-items: center !important;
        border-bottom: 1px solid #f1f5f9 !important;
        gap: 0 !important;
        transition: background-color 0.15s ease !important;
    }

    /* Header Tabel */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stHorizontalBlock"]:has(.table-header-marker),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="stHorizontalBlock"]:has(.table-header-marker) {
        border-bottom: 1.5px solid #edf2f7 !important;
        padding: 14px 24px 14px 20px !important;
    }

    /* Hover pada baris data (bukan header) */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stHorizontalBlock"]:not(:has(.table-header-marker)):hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="stHorizontalBlock"]:not(:has(.table-header-marker)):hover {
        background-color: #fafbfd !important;
    }

    /* Hilangkan border pada baris terakhir */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) > [data-testid="stHorizontalBlock"]:last-child,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) > [data-testid="stHorizontalBlock"]:last-child,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) > [data-testid="stLayoutWrapper"]:last-child [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) > [data-testid="stLayoutWrapper"]:last-child [data-testid="stHorizontalBlock"] {
        border-bottom: none !important;
    }

    /* Reset spacing internal kolom tabel */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stMarkdownContainer"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
    }

    .table-th {
        color: var(--text-table-head);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        line-height: 1.4;
    }

    .table-th-center {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stMarkdownContainer"]:has(.table-th-center),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="stMarkdownContainer"]:has(.table-th-center) {
        width: 100% !important;
        text-align: center !important;
    }

    .program-name-cell {
        font-size: 14.5px;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.5;
    }

    .badge-level {
        background-color: #e6f0ff;
        color: #2b6cb0;
        font-weight: 700;
        font-size: 12px;
        padding: 4px 14px;
        border-radius: 9999px;
        display: inline-block;
        letter-spacing: 0.2px;
        line-height: 1.4;
        white-space: nowrap;
    }

    .badge-level.badge-pra {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
    }

    .badge-level.badge-sd {
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }

    .badge-level.badge-smp {
        background-color: #ede9fe;
        color: #6d28d9;
        border: 1px solid #ddd6fe;
    }

    .badge-level.badge-sma {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }

    .session-count {
        font-size: 14px;
        color: #334155;
        font-weight: 500;
        line-height: 1.5;
    }

    .table-text-cell {
        font-size: 14.5px;
        color: #1e293b;
        line-height: 1.5;
    }

    .badge-status {
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        letter-spacing: 0.2px;
        line-height: 1.4;
    }

    .badge-status-aktif {
        background-color: #e6f4ea;
        color: #137333;
    }

    .badge-status-nonaktif {
        background-color: #e8ecf2;
        color: #475569;
    }

    .badge-status-lunas {
        background-color: #e6f4ea;
        color: #137333;
    }

    .badge-status-belum {
        background-color: #fef7e0;
        color: #92400e;
    }

    .badge-status-menunggak {
        background-color: #fce8e6;
        color: #c5221f;
    }

    .badge-inhal-st {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 6px;
        display: inline-block;
        margin-left: 6px;
    }

    /* Card putih untuk kontainer non-form (misal Card Periode Tagihan) */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .card-box-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .card-box-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .card-box-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="element-container"] .card-box-marker) {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker),
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
    }

    [data-testid="stElementContainer"]:has(.card-box-marker),
    [data-testid="element-container"]:has(.card-box-marker) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) [data-testid="stHorizontalBlock"] {
        align-items: flex-end !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) [data-testid="stWidgetLabel"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) [data-testid="stWidgetLabel"] p {
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) div[data-baseweb="select"] > div,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        height: 44px !important;
        min-height: 44px !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[kind="primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[data-testid="baseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[data-testid="stBaseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[kind="primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[data-testid="baseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[data-testid="stBaseButton-primary"] {
        background-color: var(--primary-blue) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
        height: 44px !important;
        min-height: 44px !important;
        padding: 0 24px !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        white-space: nowrap !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[kind="primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[data-testid="baseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-box-marker) button[data-testid="stBaseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[kind="primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[data-testid="baseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .card-box-marker) button[data-testid="stBaseButton-primary"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14.5px !important;
        margin: 0 !important;
    }

    /* Stat Cards Pembayaran */
    .stat-card {
        border-radius: 16px;
        padding: 16px 22px;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 18px;
    }
    .stat-label {
        font-size: 11.5px;
        font-weight: 800;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
    }
    .stat-card-lunas {
        background-color: #eaf7ee;
        color: #137333;
    }
    .stat-card-belum {
        background-color: #fef7e0;
        color: #92400e;
    }
    .stat-card-menunggak {
        background-color: #fce8e6;
        color: #c5221f;
    }

    /* Tombol Hapus rata kanan & gaya outline pill merah */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) [data-testid="stColumn"]:last-child [data-testid="stButton"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) [data-testid="column"]:last-child [data-testid="stButton"] {
        display: flex !important;
        justify-content: flex-end !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[kind="secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="baseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="stBaseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[kind="secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="baseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: var(--danger-text) !important;
        border: 1px solid var(--danger-border) !important;
        border-radius: 8px !important;
        padding: 6px 18px !important;
        min-height: 0 !important;
        height: auto !important;
        width: auto !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[kind="secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="baseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="stBaseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[kind="secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="baseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="stBaseButton-secondary"] p {
        color: var(--danger-text) !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[kind="secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[kind="secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover {
        background-color: var(--danger-bg-hover) !important;
        border-color: #f87171 !important;
        color: #b91c1c !important;
    }

    /* Tombol Edit di dalam Tabel (Pill Outline Biru) */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button:has(p:contains("Edit")),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button:has(p:contains("Edit")) {
        background: transparent !important;
        color: var(--primary-blue) !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        min-height: 0 !important;
        height: auto !important;
        width: 100% !important;
    }
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button:has(p:contains("Edit")) p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button:has(p:contains("Edit")) p {
        color: var(--primary-blue) !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button:has(p:contains("Edit")):hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button:has(p:contains("Edit")):hover {
        background-color: #eff6ff !important;
        border-color: #93c5fd !important;
        color: #1d4ed8 !important;
    }
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button:has(p:contains("Edit")):hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button:has(p:contains("Edit")):hover p {
        color: #1d4ed8 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover p {
        color: #b91c1c !important;
    }

    /* ----------------- GRID KARTU RUANG BELAJAR ----------------- */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .room-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .room-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .room-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="element-container"] .room-card-marker) {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
        margin-bottom: 16px !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker),
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px 28px !important;
        box-shadow: 0 2px 8px rgba(18, 24, 38, 0.02) !important;
        gap: 0 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker),
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    [data-testid="stElementContainer"]:has(.room-card-marker),
    [data-testid="element-container"]:has(.room-card-marker) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .room-card-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-dark);
        margin: 0 0 8px 0;
        line-height: 1.3;
    }

    .room-card-capacity {
        font-size: 14.5px;
        color: var(--text-muted);
        margin: 0 0 18px 0;
        line-height: 1.5;
    }

    .room-card-capacity strong {
        color: #1e293b;
        font-weight: 700;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-secondary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: var(--danger-text) !important;
        border: 1px solid var(--danger-border) !important;
        border-radius: 8px !important;
        padding: 6px 18px !important;
        min-height: 0 !important;
        height: auto !important;
        width: 100% !important;
        justify-content: center !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-secondary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-secondary"] p {
        color: var(--danger-text) !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-secondary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-secondary"]:hover {
        background-color: var(--danger-bg-hover) !important;
        border-color: #f87171 !important;
        color: #b91c1c !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-secondary"]:hover p {
        color: #b91c1c !important;
    }

    /* Tombol Lihat (Outline Biru) di Kartu Ruang Belajar */
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-primary"],
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-primary"] {
        background: transparent !important;
        color: var(--primary-blue) !important;
        border: 1px solid #bfdbfe !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        min-height: 0 !important;
        height: auto !important;
        width: 100% !important;
        justify-content: center !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-primary"] p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-primary"] p {
        color: var(--primary-blue) !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="primary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-primary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-primary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="primary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-primary"]:hover,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-primary"]:hover {
        background-color: #eff6ff !important;
        border-color: #60a5fa !important;
        color: var(--primary-hover) !important;
    }

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[kind="primary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="baseButton-primary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .room-card-marker) button[data-testid="stBaseButton-primary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[kind="primary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="baseButton-primary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .room-card-marker) button[data-testid="stBaseButton-primary"]:hover p {
        color: var(--primary-hover) !important;
    }

    /* Card jadwal ruang (Lihat) */
    .sched-item {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background-color: #f8fafc;
    }
    .sched-item.ongoing {
        border-color: #86efac;
        background-color: #f0fdf4;
    }
    .sched-badge-ongoing {
        background-color: #dcfce7;
        color: #15803d;
        font-size: 11.5px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .sched-badge-scheduled {
        background-color: #e0f2fe;
        color: #0369a1;
        font-size: 11.5px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

# =============================================================================
# 1B. KONFIGURASI PENGGUNA & HAK AKSES SISTEM (AUTH & RBAC)
# =============================================================================
USER_ACCOUNTS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "display_name": "Administrator",
        "badge": "Admin",
        "allowed_menus": [
            "Dashboard",
            "Siswa dan Wali",
            "Program",
            "Tutor",
            "Ruang Belajar",
            "Kelompok Belajar",
            "Jadwal",
            "Tagihan",
            "Pembayaran",
        ],
        "default_menu": "Dashboard",
    },
    "owner": {
        "password": "owner123",
        "role": "pemilik",
        "display_name": "Pemilik (Owner)",
        "badge": "Pemilik",
        "allowed_menus": ["Dashboard"],
        "default_menu": "Dashboard",
    },
    "tutor": {
        "password": "tutor123",
        "role": "tutor",
        "display_name": "Tutor Pengajar",
        "badge": "Tutor",
        "allowed_menus": ["Jadwal"],
        "default_menu": "Jadwal",
    },
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Dashboard"
if "selected_room_detail" not in st.session_state:
    st.session_state.selected_room_detail = None


# =============================================================================
# 1C. GERBANG LOGIN (LOGIN GATE) JIKA BELUM TERAUTENTIKASI
# =============================================================================
if not st.session_state.get("logged_in") or not st.session_state.get("user_info"):
    # Sembunyikan sidebar di halaman login & terapkan CSS persis gambar publik/index.html
    st.markdown("""
        <style>
            @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }

            /* Container 2-Kolom Split Card Persis Screenshot */
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) {
                max-width: 1020px !important;
                margin: 20px auto 30px auto !important;
                background: #ffffff !important;
                border-radius: 20px !important;
                border: 1px solid #e2e8f0 !important;
                box-shadow: 0 12px 40px rgba(19, 31, 56, 0.08) !important;
                overflow: hidden !important;
                gap: 0 !important;
                align-items: stretch !important;
            }

            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) > [data-testid="stColumn"]:first-child {
                background: #131f38 !important;
                padding: 44px 38px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                position: relative !important;
                overflow: hidden !important;
            }

            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) > [data-testid="stColumn"]:last-child {
                background: #ffffff !important;
                padding: 44px 42px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
            }

            /* Elemen Hero Panel Kiri */
            .brand-pill-active {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #ffffff;
                color: #131f38;
                font-weight: 700;
                font-size: 13px;
                padding: 7px 18px;
                border-radius: 9999px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
                margin-bottom: 24px;
                width: fit-content;
            }
            .brand-pill-active i {
                color: #1e50bb;
            }

            .feature-card-item {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 14px;
                padding: 14px 16px;
                margin-bottom: 12px;
                display: flex;
                align-items: flex-start;
                gap: 14px;
            }
            .feature-icon-box {
                width: 36px;
                height: 36px;
                border-radius: 10px;
                background: rgba(30, 80, 187, 0.25);
                color: #8ea3c7;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                flex-shrink: 0;
            }
            .status-dot-pulse {
                width: 8px;
                height: 8px;
                background-color: #22c55e;
                border-radius: 50%;
                box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.25);
                display: inline-block;
            }

            /* Styling Form Panel Kanan */
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) [data-testid="stForm"] {
                border: none !important;
                padding: 0 !important;
            }
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) [data-testid="stTextInput"] {
                margin-bottom: 8px !important;
            }
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) [data-testid="stTextInput"] label p {
                font-size: 13.5px !important;
                font-weight: 600 !important;
                color: #334155 !important;
                margin-bottom: 4px !important;
            }
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) [data-testid="stTextInput"] input {
                height: 48px !important;
                border-radius: 10px !important;
                border: 1px solid #cbd5e1 !important;
                font-size: 14.5px !important;
                color: #121826 !important;
                padding: 0 16px !important;
                background: #ffffff !important;
            }
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) [data-testid="stTextInput"] input:focus {
                border-color: #1e50bb !important;
                box-shadow: 0 0 0 3px rgba(30, 80, 187, 0.15) !important;
            }
            [data-testid="stHorizontalBlock"]:has(.login-card-left-marker) button[kind="primary"] {
                height: 48px !important;
                background-color: #1e50bb !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                border-radius: 10px !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(30, 80, 187, 0.22) !important;
                margin-top: 10px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 7])
    with col_left:
        hero_left_html = textwrap.dedent("""
<div class="login-card-left-marker" style="display:none;"></div>
<div style="display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
<div>
<div class="brand-pill-active">
<i class="bi bi-shield-check"></i>
<span>Portal Masuk Admin</span>
</div>
<div style="margin-bottom: 24px;">
<div style="font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
Optimatika <span style="font-weight: 500; color: #8ea3c7; font-size: 18px;">· Admin</span>
</div>
<p style="color: #8ea3c7; font-size: 13.5px; line-height: 1.6; margin-top: 8px;">
Sistem administrasi bimbingan belajar modern untuk pengelolaan jadwal, peserta didik, tutor, dan tagihan SPP.
</p>
</div>
<div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 28px;">
<div class="feature-card-item">
<div class="feature-icon-box">
<i class="bi bi-calendar2-week"></i>
</div>
<div>
<div style="font-weight: 700; font-size: 13.5px; color: #ffffff;">Jadwal Anti-Bentrok</div>
<div style="font-size: 12px; color: #8ea3c7; margin-top: 2px; line-height: 1.4;">
Otomatis memeriksa bentrok ruang belajar &amp; tutor di hari yang sama.
</div>
</div>
</div>
<div class="feature-card-item">
<div class="feature-icon-box">
<i class="bi bi-mortarboard"></i>
</div>
<div>
<div style="font-weight: 700; font-size: 13.5px; color: #ffffff;">Program &amp; Kurikulum</div>
<div style="font-size: 12px; color: #8ea3c7; margin-top: 2px; line-height: 1.4;">
Mendukung jenjang SD, SMP, SMA, hingga persiapan intensif UTBK.
</div>
</div>
</div>
<div class="feature-card-item">
<div class="feature-icon-box">
<i class="bi bi-wallet2"></i>
</div>
<div>
<div style="font-weight: 700; font-size: 13.5px; color: #ffffff;">SPP &amp; Keuangan Terdata</div>
<div style="font-size: 12px; color: #8ea3c7; margin-top: 2px; line-height: 1.4;">
Pembuatan invoice tagihan otomatis &amp; kwitansi pembayaran langsung.
</div>
</div>
</div>
</div>
</div>
<div style="padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #8ea3c7;">
<div style="display: flex; align-items: center; gap: 8px;">
<span class="status-dot-pulse"></span>
<span style="color: #8ea3c7; font-weight: 600;">Server v2.4 Online</span>
</div>
<span style="color: #64748b;">PostgreSQL &amp; SQLite</span>
</div>
</div>
""").strip()
        st.markdown(hero_left_html, unsafe_allow_html=True)

    with col_right:
        header_right_html = textwrap.dedent("""
<div>
<h2 style="font-size: 26px; font-weight: 800; color: #121826; margin-bottom: 4px; letter-spacing: -0.5px;">Masuk ke Akun</h2>
<p style="color: #64748b; font-size: 13.5px; margin-bottom: 16px; line-height: 1.5;">
Silakan masukkan username dan kata sandi pengelola untuk melanjutkan.
</p>
</div>
""").strip()
        st.markdown(header_right_html, unsafe_allow_html=True)

        with st.form("form_login_portal"):
            in_username = st.text_input("Username atau Email", placeholder="Masukkan username atau email admin")
            in_password = st.text_input("Kata Sandi", type="password", placeholder="••••••••")
            remember_me = st.checkbox("Ingat sesi masuk di perangkat ini", value=True)
            btn_submit_login = st.form_submit_button("Masuk ke Sistem →", type="primary", use_container_width=True)

            if btn_submit_login:
                user_key = (in_username or "").strip().lower()
                pass_key = (in_password or "").strip()
                if not user_key or not pass_key:
                    st.warning("Username dan kata sandi wajib diisi.")
                elif user_key in USER_ACCOUNTS and USER_ACCOUNTS[user_key]["password"] == pass_key:
                    st.session_state.logged_in = True
                    st.session_state.user_info = USER_ACCOUNTS[user_key]
                    st.session_state.active_menu = USER_ACCOUNTS[user_key]["default_menu"]
                    st.toast(f"✓ Selamat datang, {USER_ACCOUNTS[user_key]['display_name']}!", icon="🎉")
                    st.rerun()
                else:
                    st.error("Username atau kata sandi tidak cocok. Silakan periksa kembali!")

        footer_right_html = textwrap.dedent("""
<div style="background-color: #f8fafc; border: 1px solid #edf2f7; font-size: 12.5px; border-radius: 12px; padding: 14px 16px; margin-top: 18px;">
<div style="font-weight: 700; color: #475569; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
<i class="bi bi-key-fill" style="color: #1e50bb; margin-right: 4px;"></i> HAK AKSES AKUN:
</div>
<div style="display: flex; flex-direction: column; gap: 8px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div><span style="background:#e0e7ff; color:#3730a3; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 11px;">Admin</span> <code style="margin-left: 4px; font-size: 12px; color: #dc2626;">admin</code> / <code style="font-size: 12px; color: #dc2626;">admin123</code></div>
<span style="color: #64748b; font-size: 11.5px;">Semua Menu Sidebar</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<div><span style="background:#fef3c7; color:#92400e; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 11px;">Pemilik</span> <code style="margin-left: 4px; font-size: 12px; color: #dc2626;">owner</code> / <code style="font-size: 12px; color: #dc2626;">owner123</code></div>
<span style="color: #64748b; font-size: 11.5px;">Hanya Dashboard</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<div><span style="background:#dcfce7; color:#166534; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 11px;">Tutor</span> <code style="margin-left: 4px; font-size: 12px; color: #dc2626;">tutor</code> / <code style="font-size: 12px; color: #dc2626;">tutor123</code></div>
<span style="color: #64748b; font-size: 11.5px;">Hanya Jadwal Belajar</span>
</div>
</div>
</div>
<div style="margin-top: 18px; padding-top: 12px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; color: #94a3b8; font-size: 12px;">
<span>&copy; 2026 Bimbel Optimatika</span>
<span style="display: inline-flex; align-items: center; gap: 4px;">
<i class="bi bi-lock-fill" style="color: #10b981;"></i> Koneksi Terenkripsi
</span>
</div>
""").strip()
        st.markdown(footer_right_html, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# 2. ROUTE GUARD & SIDEBAR ROLE-BASED ACCESS CONTROL (RBAC)
# =============================================================================
current_user = st.session_state.get("user_info") or USER_ACCOUNTS.get("admin", {})
allowed_menus = current_user.get("allowed_menus", ["Dashboard"]) if current_user else ["Dashboard"]
user_badge = current_user.get("badge", "Admin") if current_user else "Admin"
user_name = current_user.get("display_name", "Pengguna") if current_user else "Pengguna"

# Proteksi Navigasi: Jika menu aktif tidak diizinkan untuk role saat ini, redirect paksa
if current_user and st.session_state.get("active_menu") not in allowed_menus:
    st.session_state.active_menu = current_user.get("default_menu", allowed_menus[0])
    st.rerun()

with st.sidebar:
    st.markdown(f"""
        <div class="brand-container">
            <div class="brand-title">
                Optimatika <span class="brand-sub">· {user_badge}</span>
            </div>
            <div style="font-size: 11.5px; color: #8ea3c7; margin-top: 4px; padding-left: 2px;">
                Masuk: <strong style="color: #ffffff;">{user_name}</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for item in allowed_menus:
        is_active = (st.session_state.active_menu == item)
        if st.button(
            item,
            key=f"nav_{item}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_menu = item
            st.session_state.selected_room_detail = None
            st.rerun()

    st.markdown('<div class="sidebar-footer-divider"></div>', unsafe_allow_html=True)
    if st.button("Keluar", key="btn_logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.active_menu = "Dashboard"
        st.toast("Anda telah keluar dari sesi Optimatika.")
        st.rerun()

menu = st.session_state.active_menu


# =============================================================================
# 3. KONTEN UTAMA: HALAMAN PROGRAM BELAJAR (PERSIS PUBLIC/PROGRAM.HTML)
# =============================================================================
if menu == "Program":
    # TOP HEADER
    st.markdown("""
        <div class="top-header">
            <div>
                <h1 class="page-title">Data Program Belajar</h1>
                <p class="page-subtitle">Daftar program bimbingan belajar yang terdaftar di database Neon PostgreSQL.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Daftar opsi jenjang sesuai program resmi Optimatika dari client
    PROGRAM_LEVEL_OPTIONS = [
        "Prasekolah - SD I",
        "Prasekolah - SD VI",
        "SD I - VI",
        "SMP I - III",
        "SD",
        "SMP",
        "SMA"
    ]

    # Ambil program untuk form edit atau tambah
    programs = []
    try:
        programs = database.get_programs()
    except Exception as e:
        programs = []

    editing_prog_id = st.session_state.get("editing_program_id")
    editing_prog = next((p for p in programs if p["id"] == editing_prog_id), None) if editing_prog_id else None

    if editing_prog:
        # MODE EDIT PROGRAM
        with st.form("form_edit_program"):
            st.markdown(
                f'<div class="card-heading">Edit program: <span style="color: var(--primary-blue);">{html.escape(str(editing_prog["name"]))}</span></div>',
                unsafe_allow_html=True
            )
            col1, col2, col3, col4, col5 = st.columns([3.5, 2.5, 2, 1.5, 1.5])
            with col1:
                edit_nama_prog = st.text_input("Nama program", value=str(editing_prog.get("name") or ""))
            with col2:
                cur_lvl = str(editing_prog.get("level") or "SD I - VI").strip()
                lvl_idx = 2
                for idx, opt in enumerate(PROGRAM_LEVEL_OPTIONS):
                    if opt.lower() == cur_lvl.lower():
                        lvl_idx = idx
                        break
                edit_jenjang_prog = st.selectbox("Jenjang / Tingkatan", PROGRAM_LEVEL_OPTIONS, index=lvl_idx)
            with col3:
                cur_sessions = int(editing_prog.get("sessions_per_month") or 8)
                edit_sesi_prog = st.number_input("Pertemuan per bulan", min_value=1, max_value=31, value=cur_sessions, step=1)
            with col4:
                btn_simpan_edit_prog = st.form_submit_button("Simpan", type="primary", use_container_width=True)
            with col5:
                btn_batal_edit_prog = st.form_submit_button("Batal", use_container_width=True)

            if btn_simpan_edit_prog:
                if not edit_nama_prog.strip():
                    st.warning("Nama program wajib diisi.")
                else:
                    try:
                        database.update_program(editing_prog["id"], edit_nama_prog.strip(), edit_jenjang_prog, int(edit_sesi_prog))
                        try:
                            database.sync_ke_html()
                        except Exception:
                            pass
                        st.session_state["editing_program_id"] = None
                        st.toast(f"✓ Program '{edit_nama_prog.strip()}' berhasil diperbarui di Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui program: {e}")

            if btn_batal_edit_prog:
                st.session_state["editing_program_id"] = None
                st.rerun()
    else:
        # MODE TAMBAH PROGRAM
        with st.form("form_add_program", clear_on_submit=True):
            st.markdown('<div class="card-heading">Tambah program</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([3.5, 2.5, 2, 2])
            with col1:
                nama_input = st.text_input("Nama program", placeholder="contoh: PANCA (Pandai Membaca)")
            with col2:
                jenjang_input = st.selectbox("Jenjang / Tingkatan", PROGRAM_LEVEL_OPTIONS, index=2)
            with col3:
                sesi_input = st.number_input("Pertemuan per bulan", min_value=1, max_value=31, value=8, step=1)
            with col4:
                btn_simpan = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            if btn_simpan:
                if not nama_input.strip():
                    st.warning("Nama program wajib diisi.")
                else:
                    try:
                        database.add_program(nama_input.strip(), jenjang_input, int(sesi_input))
                        try:
                            database.sync_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Program '{nama_input.strip()}' berhasil ditambahkan ke Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan program: {e}")

    # CARD 2: TABEL DATA PROGRAM (SATU CARD UTUH)
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        # Header Tabel
        th1, th2, th3, th4 = st.columns([4.0, 2.8, 1.7, 1.5])
        with th1:
            st.markdown('<div class="table-th table-header-marker">PROGRAM</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">JENJANG</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">PERTEMUAN / BULAN</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th table-th-center" style="text-align: center; width: 100%; display: block;">AKSI</div>', unsafe_allow_html=True)

        # Baris Data Program dari Neon PostgreSQL
        if not programs:
            st.markdown(
                "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                "Belum ada data program di database Neon.</p>",
                unsafe_allow_html=True,
            )
        else:
            for p in programs:
                r1, r2, r3, r4 = st.columns([4.0, 2.8, 1.7, 1.5])
                with r1:
                    safe_name = html.escape(str(p['name']))
                    st.markdown(f'<div class="program-name-cell">{safe_name}</div>', unsafe_allow_html=True)
                with r2:
                    lvl_display = str(p.get('level') or 'SD I - VI').strip()
                    lvl_upper = lvl_display.upper()
                    badge_class = "badge-level"
                    if "PRASEKOLAH" in lvl_upper or "PRA" in lvl_upper:
                        badge_class += " badge-pra"
                    elif "SMP" in lvl_upper:
                        badge_class += " badge-smp"
                    elif "SMA" in lvl_upper:
                        badge_class += " badge-sma"
                    else:
                        badge_class += " badge-sd"
                    st.markdown(f'<span class="{badge_class}">{html.escape(lvl_display)}</span>', unsafe_allow_html=True)
                with r3:
                    st.markdown(
                        f'<span class="session-count">{int(p["sessions_per_month"])}×</span>',
                        unsafe_allow_html=True,
                    )
                with r4:
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("Edit", key=f"btn_edit_prog_{p['id']}"):
                            st.session_state["editing_program_id"] = p['id']
                            st.rerun()
                    with btn_c2:
                        if st.button("Hapus", key=f"btn_del_prog_{p['id']}", type="secondary"):
                            try:
                                database.delete_program(p['id'])
                                try:
                                    database.sync_ke_html()
                                except Exception:
                                    pass
                                if st.session_state.get("editing_program_id") == p['id']:
                                    st.session_state["editing_program_id"] = None
                                st.toast(f"✓ Program '{p['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus: {e}")


# =============================================================================
# 3B. KONTEN UTAMA: HALAMAN DATA TUTOR (PERSIS PUBLIC/TUTOR.HTML + NEON CRUD)
# =============================================================================
elif menu == "Tutor":
    tutors = []
    tutor_load_error = None
    try:
        tutors = database.get_tutors()
    except Exception as e:
        tutor_load_error = e

    aktif_count = sum(1 for t in tutors if str(t.get('status', 'Aktif')).strip().lower() == 'aktif')

    # TOP HEADER
    st.markdown(f"""
        <div class="top-header">
            <div>
                <h1 class="page-title">Data Tutor</h1>
                <p class="page-subtitle">{aktif_count} tutor aktif</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Ambil daftar program langsung dari tabel programs (program.name)
    programs_for_tutor = []
    try:
        programs_for_tutor = database.get_programs()
    except Exception:
        programs_for_tutor = []

    list_mapel_options = [
        str(p['name']).strip() for p in programs_for_tutor 
        if p.get('name') and str(p.get('name')).strip() != "Matematika SD & SMP"
    ]

    # CARD 1: FORM TAMBAH / FORM EDIT TUTOR
    editing_tutor_id = st.session_state.get("editing_tutor_id")
    editing_tutor = next((t for t in tutors if t["id"] == editing_tutor_id), None) if editing_tutor_id else None

    if editing_tutor:
        # MODE EDIT TUTOR
        with st.form("form_edit_tutor"):
            st.markdown(
                f'<div class="card-heading">Edit tutor: <span style="color: var(--primary-blue);">{html.escape(str(editing_tutor["name"]))}</span></div>',
                unsafe_allow_html=True
            )
            col1, col2, col3, col4, col5 = st.columns([3.5, 3, 2.5, 1.8, 1.5])
            with col1:
                edit_nama_tutor = st.text_input("Nama tutor", value=str(editing_tutor.get("name") or ""))
            with col2:
                cur_mapel = str(editing_tutor.get("specialty") or "").strip()
                # Pilihan mata pelajaran murni hanya dari tabel programs (tanpa menyisipkan teks non-program seperti 'Matematika SD & SMP')
                edit_mapel_opts = [opt for opt in list_mapel_options if opt != "Matematika SD & SMP"]
                if not edit_mapel_opts:
                    edit_mapel_opts = ["Pilih Program..."]

                m_idx = 0
                if cur_mapel in edit_mapel_opts:
                    m_idx = edit_mapel_opts.index(cur_mapel)
                else:
                    # Jika cur_mapel adalah data lama yang tidak ada di tabel program, arahkan ke program yang relevan
                    for idx, opt in enumerate(edit_mapel_opts):
                        if "MATIK SD" in opt or "Matematika SD" in opt or "MATIK" in opt:
                            m_idx = idx
                            break
                edit_mapel_tutor = st.selectbox("Mata pelajaran (Program)", edit_mapel_opts, index=m_idx)
            with col3:
                edit_phone_tutor = st.text_input("No. telepon", value=str(editing_tutor.get("phone") or ""))
            with col4:
                cur_status = str(editing_tutor.get("status") or "Aktif").strip()
                st_idx = 1 if cur_status.lower() == "nonaktif" else 0
                edit_status_tutor = st.selectbox("Status", ["Aktif", "Nonaktif"], index=st_idx)
            with col5:
                st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
                btn_simpan_edit_tutor = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            c_batal, _ = st.columns([1.5, 8.5])
            with c_batal:
                btn_batal_edit_tutor = st.form_submit_button("Batal", use_container_width=True)

            if btn_simpan_edit_tutor:
                if not edit_nama_tutor.strip() or not edit_mapel_tutor.strip() or not edit_phone_tutor.strip():
                    st.warning("Nama tutor, mata pelajaran, dan no. telepon wajib diisi.")
                else:
                    try:
                        database.update_tutor(
                            editing_tutor["id"],
                            edit_nama_tutor.strip(),
                            edit_mapel_tutor.strip(),
                            edit_phone_tutor.strip(),
                            status=edit_status_tutor
                        )
                        try:
                            database.sync_tutor_ke_html()
                        except Exception:
                            pass
                        st.session_state["editing_tutor_id"] = None
                        st.toast(f"✓ Data tutor '{edit_nama_tutor.strip()}' berhasil diperbarui di Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui tutor: {e}")

            if btn_batal_edit_tutor:
                st.session_state["editing_tutor_id"] = None
                st.rerun()
    else:
        # MODE TAMBAH TUTOR
        with st.form("form_add_tutor", clear_on_submit=True):
            st.markdown('<div class="card-heading">Tambah tutor</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([4, 3, 3, 2])
            with col1:
                tutor_name = st.text_input("Nama tutor")
            with col2:
                add_opts = [opt for opt in list_mapel_options if opt != "Matematika SD & SMP"]
                if not add_opts:
                    add_opts = ["Pilih Program..."]
                tutor_specialty = st.selectbox("Mata pelajaran (Program)", add_opts)
            with col3:
                tutor_phone = st.text_input("No. telepon", placeholder="08...")
            with col4:
                btn_simpan_tutor = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            if btn_simpan_tutor:
                if not tutor_name.strip() or not str(tutor_specialty or "").strip() or not tutor_phone.strip():
                    st.warning("Nama tutor, mata pelajaran (program), dan no. telepon wajib diisi.")
                else:
                    try:
                        database.add_tutor(
                            tutor_name.strip(),
                            str(tutor_specialty).strip(),
                            tutor_phone.strip(),
                            status="Aktif",
                        )
                        try:
                            database.sync_tutor_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Tutor '{tutor_name.strip()}' berhasil ditambahkan ke Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan tutor: {e}")

    # CARD 2: TABEL DATA TUTOR
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        # Header Tabel
        th1, th2, th3, th4, th5 = st.columns([2.8, 2.3, 2.2, 1.0, 1.7])
        with th1:
            st.markdown('<div class="table-th table-header-marker">TUTOR</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">MATA PELAJARAN</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">TELEPON</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th">STATUS</div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="table-th table-th-center" style="text-align: center; width: 100%; display: block;">AKSI</div>', unsafe_allow_html=True)

        if tutor_load_error is not None:
            st.error(f"Gagal mengambil data tutor dari database Neon: {tutor_load_error}")
        elif not tutors:
            st.markdown(
                "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                "Belum ada data tutor di database Neon.</p>",
                unsafe_allow_html=True,
            )
        else:
            for t in tutors:
                r1, r2, r3, r4, r5 = st.columns([2.8, 2.3, 2.2, 1.0, 1.7])
                with r1:
                    st.markdown(
                        f'<div class="program-name-cell">{html.escape(str(t["name"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r2:
                    t_specialty = str(t.get("specialty") or "").strip()
                    if "matematika sd & smp" in t_specialty.lower():
                        t_specialty = next((opt for opt in list_mapel_options if "MATIK SD" in opt or "Matematika SD" in opt or "MATIK" in opt), "MATIK SD")
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(t_specialty)}</div>',
                        unsafe_allow_html=True,
                    )
                with r3:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(t["phone"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r4:
                    status = str(t.get("status") or "Aktif")
                    badge_cls = (
                        "badge-status badge-status-aktif"
                        if status.strip().lower() == "aktif"
                        else "badge-status badge-status-nonaktif"
                    )
                    st.markdown(
                        f'<span class="{badge_cls}">{html.escape(status)}</span>',
                        unsafe_allow_html=True,
                    )
                with r5:
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("Edit", key=f"btn_edit_tutor_{t['id']}"):
                            st.session_state["editing_tutor_id"] = t['id']
                            st.rerun()
                    with btn_c2:
                        if st.button("Hapus", key=f"btn_del_tutor_{t['id']}", type="secondary"):
                            try:
                                database.delete_tutor(t['id'])
                                try:
                                    database.sync_tutor_ke_html()
                                except Exception:
                                    pass
                                if st.session_state.get("editing_tutor_id") == t['id']:
                                    st.session_state["editing_tutor_id"] = None
                                st.toast(f"✓ Tutor '{t['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus tutor: {e}")


# =============================================================================
# 3C. KONTEN UTAMA: HALAMAN DATA RUANG BELAJAR & DETAIL JADWAL RUANG
# =============================================================================
elif menu == "Ruang Belajar":
    selected_room = st.session_state.get("selected_room_detail")

    # JIKA TOMBOL "LIHAT" DIKLIK -> TAMPILAN FULL PAGE SEPERTI RUANG_BELAJAR_DETAIL.HTML (REFERENSI DATA TUTOR)
    if selected_room is not None:
        room_id = selected_room["id"]
        room_label = selected_room["name"]
        room_cap = selected_room.get("capacity", 0)

        schedules = []
        sched_error = None
        try:
            schedules = database.get_room_schedules(room_id)
        except Exception as e:
            sched_error = e

        # TOP HEADER + TOMBOL KEMBALI
        h_left, h_right = st.columns([8, 2])
        with h_left:
            st.markdown(f"""
                <div class="top-header" style="margin-bottom: 18px;">
                    <div>
                        <h1 class="page-title">Jadwal Kelas · {html.escape(str(room_label))}</h1>
                        <p class="page-subtitle">Kapasitas {int(room_cap)} siswa · {len(schedules)} jadwal kelas terdaftar.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with h_right:
            st.markdown("<div style='display:flex; justify-content:flex-end; padding-top:8px;'>", unsafe_allow_html=True)
            if st.button("← Kembali", key="btn_back_to_rooms", type="secondary", use_container_width=True):
                st.session_state.selected_room_detail = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # CARD 1: FORM TAMBAH JADWAL KELAS DI RUANG INI (PERSIS GAYA DATA TUTOR)
        try:
            tutor_opts = database.get_tutors()
            program_opts = database.get_programs()
        except Exception as e:
            tutor_opts, program_opts = [], []
            st.error(f"Gagal memuat daftar tutor/program: {e}")

        with st.form(f"form_room_sched_{room_id}", clear_on_submit=False):
            st.markdown('<div class="card-heading">Tambah jadwal kelas</div>', unsafe_allow_html=True)
            f1, f2, f3, f4, f5, f6 = st.columns([3, 3, 2, 1.5, 1.5, 2])
            with f1:
                if tutor_opts:
                    sel_tutor = st.selectbox(
                        "Tutor",
                        tutor_opts,
                        format_func=lambda t: f"{t['name']} ({t['specialty']})",
                    )
                else:
                    sel_tutor = None
                    st.text_input("Tutor", value="Belum ada data tutor", disabled=True)
            with f2:
                if program_opts:
                    sel_program = st.selectbox(
                        "Mata pelajaran",
                        program_opts,
                        format_func=lambda p: f"{p['name']} ({p['level']})",
                    )
                else:
                    sel_program = None
                    st.text_input("Mata pelajaran", value="Belum ada data program", disabled=True)
            with f3:
                sel_day = st.selectbox(
                    "Hari",
                    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                )
            with f4:
                jam_mulai = st.text_input("Jam mulai", value="15:00", placeholder="15:00")
            with f5:
                jam_selesai = st.text_input("Jam berakhir", value="16:30", placeholder="16:30")
            with f6:
                btn_save_sched = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            if btn_save_sched:
                if not sel_tutor or not sel_program:
                    st.warning("Pastikan data Tutor dan Program sudah ada terlebih dahulu.")
                else:
                    try:
                        database.add_room_schedule(
                            room_id,
                            sel_tutor["id"],
                            sel_program["id"],
                            sel_day,
                            jam_mulai.strip() or "15:00",
                            jam_selesai.strip() or "16:30",
                        )
                        try:
                            database.sync_jadwal_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Jadwal kelas di {room_label} berhasil disimpan!", icon="🎉")
                        st.rerun()
                    except ValueError as ve:
                        st.warning(f"⚠️ {ve}")
                    except Exception as e:
                        st.error(f"Gagal menyimpan jadwal: {e}")

        # CARD 2: TABEL FULL-WIDTH JADWAL KELAS DI RUANG (REFERENSI GAMBAR 2)
        with st.container(border=True):
            st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

            th1, th2, th3, th4, th5, th6 = st.columns([2.4, 2.5, 1.1, 1.6, 1.2, 1.2])
            with th1:
                st.markdown('<div class="table-th table-header-marker">TUTOR</div>', unsafe_allow_html=True)
            with th2:
                st.markdown('<div class="table-th">MATA PELAJARAN</div>', unsafe_allow_html=True)
            with th3:
                st.markdown('<div class="table-th">HARI</div>', unsafe_allow_html=True)
            with th4:
                st.markdown('<div class="table-th">WAKTU</div>', unsafe_allow_html=True)
            with th5:
                st.markdown('<div class="table-th">STATUS</div>', unsafe_allow_html=True)
            with th6:
                st.markdown('<div class="table-th"></div>', unsafe_allow_html=True)

            if sched_error is not None:
                st.error(f"Gagal mengambil jadwal ruang dari database Neon: {sched_error}")
            elif not schedules:
                st.markdown(
                    "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                    "Belum ada jadwal kelas yang terdaftar di ruang ini.</p>",
                    unsafe_allow_html=True,
                )
            else:
                for s in schedules:
                    r1, r2, r3, r4, r5, r6 = st.columns([2.4, 2.5, 1.1, 1.6, 1.2, 1.2])
                    with r1:
                        st.markdown(
                            f'<div class="program-name-cell">{html.escape(str(s["tutor_name"]))}</div>',
                            unsafe_allow_html=True,
                        )
                    with r2:
                        prog = str(s.get("program_name") or "-")
                        subj = str(s.get("subject_name") or "-")
                        mapel_txt = f"{prog} ({subj})" if subj and subj != prog else prog
                        st.markdown(
                            f'<div class="table-text-cell">{html.escape(mapel_txt)}</div>',
                            unsafe_allow_html=True,
                        )
                    with r3:
                        st.markdown(
                            f'<div class="table-text-cell">{html.escape(str(s["day"]))}</div>',
                            unsafe_allow_html=True,
                        )
                    with r4:
                        st.markdown(
                            f'<div class="table-text-cell">{html.escape(str(s["start_time"]))} – {html.escape(str(s["end_time"]))}</div>',
                            unsafe_allow_html=True,
                        )
                    with r5:
                        ongoing = bool(s.get("is_ongoing"))
                        if ongoing:
                            st.markdown('<span class="badge-status badge-status-aktif">Berlangsung</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="badge-level">Terjadwal</span>', unsafe_allow_html=True)
                    with r6:
                        if st.button("Hapus", key=f"btn_del_sched_{room_id}_{s['schedule_id']}", type="secondary"):
                            try:
                                database.delete_room_schedule(s["schedule_id"])
                                try:
                                    database.sync_jadwal_ke_html()
                                except Exception:
                                    pass
                                st.toast("✓ Jadwal ruang dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus jadwal: {e}")

    # HALAMAN GRID RUANG BELAJAR (DEFAULT)
    else:
        st.markdown("""
            <div class="top-header">
                <div>
                    <h1 class="page-title">Data Ruang Belajar</h1>
                    <p class="page-subtitle">Kapasitas ruang dipakai untuk memeriksa jadwal dan jumlah anggota kelompok.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # CARD 1: FORM TAMBAH RUANG
        with st.form("form_add_room", clear_on_submit=True):
            st.markdown('<div class="card-heading">Tambah ruang</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([5, 4, 3])
            with col1:
                room_name = st.text_input("Nama ruang", placeholder="contoh: Ruang C")
            with col2:
                room_capacity = st.number_input("Kapasitas (siswa)", min_value=1, max_value=200, value=5, step=1)
            with col3:
                btn_simpan_room = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            if btn_simpan_room:
                if not room_name.strip():
                    st.warning("Nama ruang wajib diisi.")
                else:
                    try:
                        database.add_room(room_name.strip(), int(room_capacity))
                        try:
                            database.sync_ruang_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Ruang '{room_name.strip()}' berhasil ditambahkan ke Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan ruang: {e}")

        # GRID KARTU DAFTAR RUANG BELAJAR
        try:
            rooms = database.get_rooms()
            if not rooms:
                st.markdown(
                    "<div style='background:#ffffff; border:1px solid #f0f4f8; border-radius:16px; padding:28px 20px; text-align:center; color:#64748b;'>"
                    "Belum ada data ruang belajar di database Neon.</div>",
                    unsafe_allow_html=True,
                )
            else:
                for i in range(0, len(rooms), 4):
                    cols = st.columns(4)
                    for col, room in zip(cols, rooms[i:i + 4]):
                        with col:
                            with st.container(border=True):
                                st.markdown('<div class="room-card-marker"></div>', unsafe_allow_html=True)
                                st.markdown(
                                    f'<div class="room-card-title">{html.escape(str(room["name"]))}</div>'
                                    f'<div class="room-card-capacity">Kapasitas <strong>{int(room["capacity"])}</strong> siswa</div>',
                                    unsafe_allow_html=True,
                                )
                                btn_col1, btn_col2 = st.columns(2, gap="small")
                                with btn_col1:
                                    if st.button(
                                        "Lihat",
                                        key=f"btn_view_room_{room['id']}",
                                        type="primary",
                                        use_container_width=True,
                                    ):
                                        st.session_state.selected_room_detail = {
                                            "id": room["id"],
                                            "name": room["name"],
                                            "capacity": room["capacity"],
                                        }
                                        st.rerun()
                                with btn_col2:
                                    if st.button(
                                        "Hapus",
                                        key=f"btn_del_room_{room['id']}",
                                        type="secondary",
                                        use_container_width=True,
                                    ):
                                        try:
                                            database.delete_room(room['id'])
                                            try:
                                                database.sync_ruang_ke_html()
                                                database.sync_jadwal_ke_html()
                                            except Exception:
                                                pass
                                            st.toast(f"✓ Ruang '{room['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Gagal menghapus ruang: {e}")
        except Exception as e:
            st.error(f"Gagal mengambil data ruang belajar dari database Neon: {e}")


# =============================================================================
# 3D. KONTEN UTAMA: HALAMAN JADWAL BELAJAR (TERHUBUNG KE RUANG & TUTOR DI NEON)
# =============================================================================
elif menu == "Jadwal":
    # TOP HEADER
    st.markdown("""
        <div class="top-header">
            <div>
                <h1 class="page-title">Jadwal Belajar</h1>
                <p class="page-subtitle">Sebelum disimpan, sistem memeriksa bentrok ruang dan tutor pada hari yang sama.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        program_opts = database.get_programs()
        tutor_opts = database.get_tutors()
        room_opts = database.get_rooms()
        all_schedules = database.get_all_schedules()
    except Exception as e:
        program_opts, tutor_opts, room_opts, all_schedules = [], [], [], []
        st.error(f"Gagal memuat data Program/Tutor/Ruang dari Neon: {e}")

    # CARD 1: FORM TAMBAH / FORM EDIT JADWAL
    editing_sched_id = st.session_state.get("editing_schedule_id")
    editing_sched = next((s for s in all_schedules if s["schedule_id"] == editing_sched_id), None) if editing_sched_id else None

    if editing_sched:
        # MODE EDIT JADWAL
        with st.form("form_edit_schedule"):
            st.markdown(
                f'<div class="card-heading">Edit jadwal: <span style="color: var(--primary-blue);">{html.escape(str(editing_sched.get("day")))} ({html.escape(str(editing_sched.get("program_name") or editing_sched.get("group_name") or "-"))})</span></div>',
                unsafe_allow_html=True
            )
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                prog_ids = [p["id"] for p in program_opts]
                cur_prog_id = editing_sched.get("program_id")
                p_idx = prog_ids.index(cur_prog_id) if cur_prog_id in prog_ids else 0
                edit_sel_prog = st.selectbox(
                    "Kelompok / Program",
                    program_opts,
                    index=p_idx if program_opts else 0,
                    format_func=lambda p: f"{p['name']} ({p['level']})",
                ) if program_opts else None
            with c2:
                tutor_ids = [t["id"] for t in tutor_opts]
                cur_tutor_id = editing_sched.get("tutor_id")
                t_idx = tutor_ids.index(cur_tutor_id) if cur_tutor_id in tutor_ids else 0
                edit_sel_tutor = st.selectbox(
                    "Tutor",
                    tutor_opts,
                    index=t_idx if tutor_opts else 0,
                    format_func=lambda t: t["name"],
                ) if tutor_opts else None
            with c3:
                room_ids = [r["id"] for r in room_opts]
                cur_room_id = editing_sched.get("room_id")
                r_idx = room_ids.index(cur_room_id) if cur_room_id in room_ids else 0
                edit_sel_room = st.selectbox(
                    "Ruang",
                    room_opts,
                    index=r_idx if room_opts else 0,
                    format_func=lambda r: r["name"],
                ) if room_opts else None
            with c4:
                days_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                cur_day = str(editing_sched.get("day") or "Senin")
                d_idx = days_list.index(cur_day) if cur_day in days_list else 0
                edit_sel_hari = st.selectbox("Hari", days_list, index=d_idx)
            with c5:
                edit_jam_mulai = st.text_input("Mulai", value=str(editing_sched.get("start_time") or "15:00"))

            s1, s2, _ = st.columns([1.5, 1.5, 4])
            with s1:
                edit_jam_selesai = st.text_input("Selesai", value=str(editing_sched.get("end_time") or "16:30"))
            with s2:
                st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
                btn_simpan_edit_jadwal = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            c_batal, _ = st.columns([1.5, 8.5])
            with c_batal:
                btn_batal_edit_jadwal = st.form_submit_button("Batal", use_container_width=True)

            if btn_simpan_edit_jadwal:
                if not edit_sel_prog or not edit_sel_tutor or not edit_sel_room:
                    st.warning("Pastikan data Program, Tutor, dan Ruang Belajar sudah dipilih.")
                else:
                    try:
                        database.update_schedule(
                            editing_sched["schedule_id"],
                            edit_sel_room["id"],
                            edit_sel_tutor["id"],
                            edit_sel_prog["id"],
                            edit_sel_hari,
                            edit_jam_mulai.strip() or "15:00",
                            edit_jam_selesai.strip() or "16:30",
                        )
                        try:
                            database.sync_jadwal_ke_html()
                        except Exception:
                            pass
                        st.session_state["editing_schedule_id"] = None
                        st.toast(
                            f"✓ Jadwal {edit_sel_prog['name']} di {edit_sel_room['name']} ({edit_sel_hari}, {edit_jam_mulai.strip()}–{edit_jam_selesai.strip()}) diperbarui!",
                            icon="🎉",
                        )
                        st.rerun()
                    except ValueError as ve:
                        st.warning(f"⚠️ {ve}")
                    except Exception as e:
                        st.error(f"Gagal memperbarui jadwal: {e}")

            if btn_batal_edit_jadwal:
                st.session_state["editing_schedule_id"] = None
                st.rerun()
    else:
        # MODE TAMBAH JADWAL (PERSIS PUBLIC/JADWAL.HTML)
        with st.form("form_add_schedule", clear_on_submit=False):
            st.markdown('<div class="card-heading">Tambah jadwal</div>', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                if program_opts:
                    sel_prog = st.selectbox(
                        "Kelompok",
                        program_opts,
                        format_func=lambda p: f"{p['name']} ({p['level']})",
                    )
                else:
                    sel_prog = None
                    st.text_input("Kelompok", value="Belum ada program", disabled=True)
            with c2:
                if tutor_opts:
                    sel_tutor = st.selectbox(
                        "Tutor",
                        tutor_opts,
                        format_func=lambda t: t["name"],
                    )
                else:
                    sel_tutor = None
                    st.text_input("Tutor", value="Belum ada tutor", disabled=True)
            with c3:
                if room_opts:
                    sel_room = st.selectbox(
                        "Ruang",
                        room_opts,
                        format_func=lambda r: r["name"],
                    )
                else:
                    sel_room = None
                    st.text_input("Ruang", value="Belum ada ruang", disabled=True)
            with c4:
                sel_hari = st.selectbox(
                    "Hari",
                    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                )
            with c5:
                jam_mulai = st.text_input("Mulai", value="15:00", placeholder="15:00")

            s1, _ = st.columns([1, 4])
            with s1:
                jam_selesai = st.text_input("Selesai", value="16:30", placeholder="16:30")

            btn_simpan_jadwal = st.form_submit_button("Periksa dan simpan", type="primary")

            if btn_simpan_jadwal:
                if not sel_prog or not sel_tutor or not sel_room:
                    st.warning("Pastikan data Program, Tutor, dan Ruang Belajar sudah tersedia di Neon.")
                else:
                    try:
                        database.add_schedule(
                            sel_room["id"],
                            sel_tutor["id"],
                            sel_prog["id"],
                            sel_hari,
                            jam_mulai.strip() or "15:00",
                            jam_selesai.strip() or "16:30",
                        )
                        try:
                            database.sync_jadwal_ke_html()
                        except Exception:
                            pass
                        st.toast(
                            f"✓ Jadwal {sel_prog['name']} di {sel_room['name']} ({sel_hari}, {jam_mulai.strip()}–{jam_selesai.strip()}) tersimpan!",
                            icon="🎉",
                        )
                        st.rerun()
                    except ValueError as ve:
                        st.warning(f"⚠️ {ve}")
                    except Exception as e:
                        st.error(f"Gagal menyimpan jadwal: {e}")

    # CARD 2: TABEL DATA JADWAL (PERSIS PUBLIC/JADWAL.HTML)
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        th1, th2, th3, th4, th5, th6 = st.columns([1.3, 1.7, 2.3, 1.9, 1.1, 1.7])
        with th1:
            st.markdown('<div class="table-th table-header-marker">HARI</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">WAKTU</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">KELOMPOK</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th">TUTOR</div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="table-th">RUANG</div>', unsafe_allow_html=True)
        with th6:
            st.markdown('<div class="table-th table-th-center" style="text-align: center; width: 100%; display: block;">AKSI</div>', unsafe_allow_html=True)

        if not all_schedules:
            st.markdown(
                "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                "Belum ada data jadwal belajar di database Neon.</p>",
                unsafe_allow_html=True,
            )
        else:
            for s in all_schedules:
                r1, r2, r3, r4, r5, r6 = st.columns([1.3, 1.7, 2.3, 1.9, 1.1, 1.7])
                with r1:
                    st.markdown(
                        f'<div class="program-name-cell">{html.escape(str(s["day"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r2:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(s["start_time"]))}–{html.escape(str(s["end_time"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r3:
                    kelompok_txt = str(s.get("program_name") or s.get("group_name") or "-")
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(kelompok_txt)}</div>',
                        unsafe_allow_html=True,
                    )
                with r4:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(s["tutor_name"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r5:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(s["room_name"]))}</div>',
                        unsafe_allow_html=True,
                    )
                with r6:
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("Edit", key=f"btn_edit_jadwal_{s['schedule_id']}"):
                            st.session_state["editing_schedule_id"] = s["schedule_id"]
                            st.rerun()
                    with btn_c2:
                        if st.button("Hapus", key=f"btn_del_jadwal_{s['schedule_id']}", type="secondary"):
                            try:
                                database.delete_schedule(s["schedule_id"])
                                try:
                                    database.sync_jadwal_ke_html()
                                except Exception:
                                    pass
                                if st.session_state.get("editing_schedule_id") == s["schedule_id"]:
                                    st.session_state["editing_schedule_id"] = None
                                st.toast("✓ Jadwal berhasil dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus jadwal: {e}")


# =============================================================================
# 3E. KONTEN UTAMA: HALAMAN TERBITKAN TAGIHAN (PERSIS PUBLIC/TAGIHAN.HTML)
# =============================================================================
elif menu == "Tagihan":
    # TOP HEADER (PERSIS GAMBAR REFERENSI)
    st.markdown("""
        <div class="top-header">
            <div>
                <h1 class="page-title">Terbitkan Tagihan</h1>
                <p class="page-subtitle">Nominal diambil dari tarif program yang diikuti tiap siswa.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CARD 1: FORM PERIODE & TOMBOL TERBITKAN (Ganti periode langsung update tabel)
    with st.container(border=True):
        st.markdown('<div class="card-box-marker"></div>', unsafe_allow_html=True)
        c_p1, c_p2, _ = st.columns([5, 3, 4])
        with c_p1:
            sel_periode = st.selectbox(
                "Periode tagihan",
                ["Oktober 2026", "November 2026", "Desember 2026"],
                key="tagihan_periode_select",
            )
        with c_p2:
            btn_terbitkan = st.button("Terbitkan untuk semua siswa", key="btn_terbitkan_tagihan", type="primary")

        if btn_terbitkan:
            try:
                published = database.publish_bills_for_period(sel_periode)
                try:
                    database.sync_tagihan_ke_html(sel_periode)
                    database.sync_pembayaran_ke_html()
                except Exception:
                    pass
                st.toast(f"✓ Tagihan periode {sel_periode} berhasil diterbitkan untuk {len(published)} siswa!", icon="🎉")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menerbitkan tagihan: {e}")

    # CARD 2: TABEL DAFTAR TAGIHAN PERIODE
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        th1, th2, th3, th4, th5 = st.columns([2.5, 2.5, 2.0, 1.5, 1.5])
        with th1:
            st.markdown('<div class="table-th table-header-marker">NO. TAGIHAN</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">SISWA</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">PROGRAM</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th">PERIODE</div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="table-th" style="text-align:right;">NOMINAL</div>', unsafe_allow_html=True)

        try:
            period_bills = database.get_bills_by_period(sel_periode)
            if not period_bills:
                st.markdown(
                    "<p style='text-align: center; color: #64748b; padding: 48px 20px; margin: 0; font-size: 14.5px;'>"
                    "Belum ada tagihan pada periode ini.</p>",
                    unsafe_allow_html=True,
                )
            else:
                for b in period_bills:
                    r1, r2, r3, r4, r5 = st.columns([2.5, 2.5, 2.0, 1.5, 1.5])
                    with r1:
                        st.markdown(
                            f'<code style="font-size:13px; color:#d63384;">{html.escape(b["invoice_no"])}</code>',
                            unsafe_allow_html=True,
                        )
                    with r2:
                        badge_status = (
                            '<span class="badge-status badge-status-lunas" style="font-size: 11px; padding: 2px 8px; margin-left: 6px;">Sudah Bayar</span>'
                            if b.get("is_lunas")
                            else '<span class="badge-status badge-status-belum" style="font-size: 11px; padding: 2px 8px; margin-left: 6px;">Belum Bayar</span>'
                        )
                        st.markdown(
                            f'<div class="program-name-cell">{html.escape(b["student_name"])} {badge_status}</div>',
                            unsafe_allow_html=True,
                        )
                    with r3:
                        st.markdown(
                            f'<div class="table-text-cell">{html.escape(b["program_name"])}</div>',
                            unsafe_allow_html=True,
                        )
                    with r4:
                        st.markdown(
                            f'<div class="table-text-cell">{html.escape(str(b.get("period") or sel_periode))}</div>',
                            unsafe_allow_html=True,
                        )
                    with r5:
                        amt = b.get("total_amount") or b.get("amount") or 0
                        st.markdown(
                            f'<div class="program-name-cell" style="text-align:right;">{database.format_rupiah(amt)}</div>',
                            unsafe_allow_html=True,
                        )
        except Exception as e:
            st.error(f"Gagal mengambil data tagihan periode dari database Neon: {e}")


# =============================================================================
# 3F. KONTEN UTAMA: HALAMAN CATAT PEMBAYARAN (CRUD KE NEON POSTGRESQL)
# =============================================================================
elif menu == "Pembayaran":
    st.markdown("""
        <div class="top-header">
            <div>
                <h1 class="page-title">Catat Pembayaran</h1>
                <p class="page-subtitle">Status dihitung dari total bayar dan jatuh tempo secara real-time di Neon PostgreSQL.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    summary = {"bills": [], "stats": {"lunas": 0, "belum_lunas": 0, "menunggak": 0}}
    pay_load_err = None
    try:
        summary = database.get_billing_summary()
    except Exception as e:
        pay_load_err = e

    bills = summary["bills"]
    stats = summary["stats"]

    # 3 Kartu Ringkasan
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""
            <div class="stat-card stat-card-lunas">
                <div class="stat-label">LUNAS</div>
                <div class="stat-value">{stats['lunas']}</div>
            </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
            <div class="stat-card stat-card-belum">
                <div class="stat-label">BELUM LUNAS</div>
                <div class="stat-value">{stats['belum_lunas']}</div>
            </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
            <div class="stat-card stat-card-menunggak">
                <div class="stat-label">MENUNGGAK</div>
                <div class="stat-value">{stats['menunggak']}</div>
            </div>
        """, unsafe_allow_html=True)

    # CARD 1: FORM CATAT PEMBAYARAN
    with st.form("form_add_payment", clear_on_submit=True):
        st.markdown('<div class="card-heading">Catat pembayaran</div>', unsafe_allow_html=True)
        p1, p2, p3 = st.columns([5, 4, 3])
        with p1:
            if bills:
                sel_bill = st.selectbox(
                    "Tagihan",
                    bills,
                    format_func=lambda b: f"{b['student_name']} · sisa {database.format_rupiah(b['remaining_amount'])}",
                )
            else:
                sel_bill = None
                st.text_input("Tagihan", value="Belum ada tagihan", disabled=True)
        with p2:
            pay_amount = st.number_input("Jumlah dibayar (Rp)", min_value=0, value=0, step=10000)
        with p3:
            btn_catat = st.form_submit_button("Catat pembayaran", type="primary", use_container_width=True)

        if btn_catat:
            if not sel_bill:
                st.warning("Tidak ada tagihan yang dipilih.")
            elif int(pay_amount) <= 0:
                st.warning("Masukkan nominal pembayaran lebih dari Rp 0.")
            else:
                try:
                    database.add_payment(sel_bill["bill_id"], int(pay_amount))
                    try:
                        database.sync_pembayaran_ke_html()
                        database.sync_tagihan_ke_html()
                    except Exception:
                        pass
                    st.toast(f"✓ Pembayaran untuk {sel_bill['student_name']} berhasil dicatat ke Neon!", icon="🎉")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal mencatat pembayaran: {e}")

    # Tambah Tagihan Siswa Baru (Opsional)
    with st.expander("+ Buat Tagihan Siswa Baru"):
        with st.form("form_add_bill", clear_on_submit=True):
            b1, b2, b3, b4 = st.columns([3, 3, 2, 2])
            with b1:
                new_student = st.text_input("Nama siswa", placeholder="contoh: Budi Santoso")
            with b2:
                new_program = st.text_input("Program", placeholder="contoh: Matematika SD")
            with b3:
                new_amount = st.number_input("Nominal (Rp)", min_value=1000, value=250000, step=10000)
            with b4:
                new_due = st.date_input("Jatuh tempo")
            if st.form_submit_button("Simpan Tagihan", type="primary"):
                if not new_student.strip():
                    st.warning("Nama siswa wajib diisi.")
                else:
                    try:
                        database.add_bill(new_student.strip(), new_program.strip(), int(new_amount), due_date=new_due)
                        try:
                            database.sync_pembayaran_ke_html()
                            database.sync_tagihan_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Tagihan baru untuk {new_student.strip()} ditambahkan!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan tagihan: {e}")

    # CARD 2: TABEL DATA PEMBAYARAN
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        th1, th2, th3, th4, th5, th6, th7 = st.columns([2.0, 1.4, 1.4, 1.4, 1.4, 1.2, 1.2])
        with th1:
            st.markdown('<div class="table-th table-header-marker">SISWA</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">JATUH TEMPO</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">TAGIHAN</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th">DIBAYAR</div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="table-th">SISA</div>', unsafe_allow_html=True)
        with th6:
            st.markdown('<div class="table-th">STATUS</div>', unsafe_allow_html=True)
        with th7:
            st.markdown('<div class="table-th"></div>', unsafe_allow_html=True)

        if pay_load_err is not None:
            st.error(f"Gagal mengambil data pembayaran dari Neon: {pay_load_err}")
        elif not bills:
            st.markdown(
                "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                "Belum ada data tagihan pembayaran di database Neon.</p>",
                unsafe_allow_html=True,
            )
        else:
            for b in bills:
                r1, r2, r3, r4, r5, r6, r7 = st.columns([2.0, 1.4, 1.4, 1.4, 1.4, 1.2, 1.2])
                with r1:
                    st.markdown(f'<div class="program-name-cell">{html.escape(b["student_name"])}</div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div class="table-text-cell">{html.escape(b["due_date_str"])}</div>', unsafe_allow_html=True)
                with r3:
                    st.markdown(f'<div class="table-text-cell">{database.format_rupiah(b["total_amount"])}</div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div class="table-text-cell">{database.format_rupiah(b["paid_amount"])}</div>', unsafe_allow_html=True)
                with r5:
                    st.markdown(f'<div class="table-text-cell">{database.format_rupiah(b["remaining_amount"])}</div>', unsafe_allow_html=True)
                with r6:
                    st.markdown(f'<span class="{html.escape(b["badge_class"])}">{html.escape(b["status"])}</span>', unsafe_allow_html=True)
                with r7:
                    btn_lbl = "Reset" if b["paid_amount"] > 0 else "Hapus"
                    if st.button(btn_lbl, key=f"btn_del_pay_{b['bill_id']}", type="secondary"):
                        try:
                            database.delete_bill_payment(b["bill_id"])
                            try:
                                database.sync_pembayaran_ke_html()
                                database.sync_tagihan_ke_html()
                            except Exception:
                                pass
                            st.toast(f"✓ Data pembayaran {b['student_name']} diperbarui!", icon="🗑️")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memproses: {e}")


# =============================================================================
# 3G. KONTEN UTAMA: HALAMAN SISWA DAN WALI (PERSIS PUBLIC/SISWA.HTML + CRUD NEON)
# =============================================================================
elif menu == "Siswa dan Wali":
    students = []
    student_load_error = None
    try:
        students = database.get_students()
    except Exception as e:
        student_load_error = e

    total_siswa = len(students)

    # TOP HEADER & KOTAK PENCARIAN (PERSIS PUBLIC/SISWA.HTML)
    head_col1, head_col2 = st.columns([3.2, 1.3])
    with head_col1:
        st.markdown(f"""
            <div class="top-header" style="margin-bottom: 0;">
                <div>
                    <h1 class="page-title">Data Siswa dan Orang Tua/Wali</h1>
                    <p class="page-subtitle">{total_siswa} siswa terdaftar</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with head_col2:
        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        search_query = st.text_input(
            "Cari siswa",
            placeholder="Cari nama siswa atau wali...",
            label_visibility="collapsed",
            key="search_siswa_input"
        )

    # CARD 1: FORM TAMBAH / FORM EDIT SISWA
    editing_id = st.session_state.get("editing_student_id")
    editing_student = next((s for s in students if s["id"] == editing_id), None) if editing_id else None

    if editing_student:
        # MODE EDIT DATA SISWA
        with st.form("form_edit_student"):
            st.markdown(
                f'<div class="card-heading">Edit data siswa: <span style="color: var(--primary-blue);">{html.escape(str(editing_student["name"]))}</span></div>',
                unsafe_allow_html=True
            )
            col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
            with col1:
                edit_nama = st.text_input("Nama siswa", value=str(editing_student.get("name") or ""))
            with col2:
                cur_lvl = str(editing_student.get("level") or "SD").upper()
                lvl_idx = ["SD", "SMP", "SMA"].index(cur_lvl) if cur_lvl in ["SD", "SMP", "SMA"] else 0
                edit_jenjang = st.selectbox("Jenjang", ["SD", "SMP", "SMA"], index=lvl_idx)
            with col3:
                edit_wali = st.text_input("Nama orang tua/wali", value=str(editing_student.get("guardian_name") or ""))
            with col4:
                edit_telp = st.text_input("No. telepon wali", value=str(editing_student.get("phone") or ""))

            btn_col1, btn_col2, _ = st.columns([2, 1.5, 4.5])
            with btn_col1:
                btn_simpan_edit = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)
            with btn_col2:
                btn_batal_edit = st.form_submit_button("Batal", use_container_width=True)

            if btn_simpan_edit:
                if not edit_nama.strip() or not edit_wali.strip() or not edit_telp.strip():
                    st.warning("Nama siswa, jenjang, wali, dan no. telepon wajib diisi.")
                else:
                    try:
                        database.update_student(
                            editing_student["id"],
                            name=edit_nama.strip(),
                            level=edit_jenjang,
                            guardian_name=edit_wali.strip(),
                            phone=edit_telp.strip()
                        )
                        try:
                            database.sync_siswa_ke_html()
                        except Exception:
                            pass
                        st.session_state["editing_student_id"] = None
                        st.toast(f"✓ Data siswa '{edit_nama.strip()}' berhasil diperbarui di Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data siswa: {e}")

            if btn_batal_edit:
                st.session_state["editing_student_id"] = None
                st.rerun()
    else:
        # MODE TAMBAH SISWA BARU
        with st.form("form_add_student", clear_on_submit=True):
            st.markdown('<div class="card-heading">Tambah siswa baru</div>', unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns([3.2, 1.8, 3.0, 2.2, 1.8])
            with col1:
                nama_siswa_baru = st.text_input("Nama siswa", placeholder="contoh: Alya Putri")
            with col2:
                jenjang_siswa_baru = st.selectbox("Jenjang", ["SD", "SMP", "SMA"])
            with col3:
                wali_siswa_baru = st.text_input("Nama orang tua/wali", placeholder="contoh: Ibu Ratna")
            with col4:
                telp_siswa_baru = st.text_input("No. telepon wali", placeholder="08...")
            with col5:
                btn_simpan_siswa = st.form_submit_button("Simpan", type="primary", use_container_width=True)

            if btn_simpan_siswa:
                if not nama_siswa_baru.strip() or not wali_siswa_baru.strip() or not telp_siswa_baru.strip():
                    st.warning("Nama siswa, jenjang, nama orang tua/wali, dan no. telepon wajib diisi.")
                else:
                    try:
                        database.add_student(
                            nama_siswa_baru.strip(),
                            level=jenjang_siswa_baru,
                            guardian_name=wali_siswa_baru.strip(),
                            phone=telp_siswa_baru.strip()
                        )
                        try:
                            database.sync_siswa_ke_html()
                        except Exception:
                            pass
                        st.toast(f"✓ Siswa '{nama_siswa_baru.strip()}' berhasil ditambahkan ke Neon!", icon="🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan siswa: {e}")

    # FILTER PENCARIAN
    display_students = students
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        display_students = [
            s for s in students
            if q in str(s.get("name", "")).lower()
            or q in str(s.get("guardian_name", "")).lower()
            or q in str(s.get("phone", "")).lower()
            or q in str(s.get("nis", "")).lower()
            or q in str(s.get("level", "")).lower()
        ]

    # CARD 2: TABEL DATA SISWA
    with st.container(border=True):
        st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)

        # Header Tabel
        th1, th2, th3, th4, th5 = st.columns([3.0, 1.5, 2.6, 2.1, 1.8])
        with th1:
            st.markdown('<div class="table-th table-header-marker">SISWA</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">JENJANG</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">ORANG TUA/WALI</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th">TELEPON</div>', unsafe_allow_html=True)
        with th5:
            st.markdown('<div class="table-th table-th-center" style="text-align: center; width: 100%; display: block;">AKSI</div>', unsafe_allow_html=True)

        if student_load_error is not None:
            st.error(f"Gagal mengambil data siswa dari database Neon: {student_load_error}")
        elif not display_students:
            msg = "Tidak ada siswa yang cocok dengan pencarian." if search_query else "Belum ada data siswa di database Neon."
            st.markdown(
                f"<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>{msg}</p>",
                unsafe_allow_html=True,
            )
        else:
            for s in display_students:
                r1, r2, r3, r4, r5 = st.columns([3.0, 1.5, 2.6, 2.1, 1.8])
                with r1:
                    safe_name = html.escape(str(s["name"]))
                    safe_nis = html.escape(str(s.get("nis") or ""))
                    nis_html = f' <span style="font-size: 11px; color: #94a3b8; font-weight: normal;">({safe_nis})</span>' if safe_nis else ""
                    st.markdown(f'<div class="program-name-cell">{safe_name}{nis_html}</div>', unsafe_allow_html=True)
                with r2:
                    lvl = str(s.get("level") or "SD").upper()
                    badge_class = "badge-level"
                    if lvl == "SMP":
                        badge_class += " badge-smp"
                    elif lvl == "SMA":
                        badge_class += " badge-sma"
                    st.markdown(f'<span class="{badge_class}">{html.escape(lvl)}</span>', unsafe_allow_html=True)
                with r3:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(s.get("guardian_name") or "-"))}</div>',
                        unsafe_allow_html=True,
                    )
                with r4:
                    st.markdown(
                        f'<div class="table-text-cell">{html.escape(str(s.get("phone") or "-"))}</div>',
                        unsafe_allow_html=True,
                    )
                with r5:
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("Edit", key=f"btn_edit_student_{s['id']}"):
                            st.session_state["editing_student_id"] = s["id"]
                            st.rerun()
                    with btn_c2:
                        if st.button("Hapus", key=f"btn_del_student_{s['id']}", type="secondary"):
                            try:
                                database.delete_student(s["id"])
                                try:
                                    database.sync_siswa_ke_html()
                                except Exception:
                                    pass
                                if st.session_state.get("editing_student_id") == s["id"]:
                                    st.session_state["editing_student_id"] = None
                                st.toast(f"✓ Siswa '{s['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus siswa: {e}")


# =============================================================================
# 3H. KONTEN UTAMA: HALAMAN KELOMPOK BELAJAR & KONSULTASI JADWAL PENGGANTI (INHAL)
# =============================================================================
elif menu == "Kelompok Belajar":
    # 1. Inisialisasi State Kelompok & Inhal jika belum ada
    if "kelompok_state" not in st.session_state:
        st.session_state["kelompok_state"] = {
            "matematika": [
                {"name": "Dimas Aditya", "isInhal": False},
                {"name": "Fikri Ramadhan", "isInhal": False},
                {"name": "Citra Maharani", "isInhal": False},
            ],
            "calistung": [
                {"name": "Alya Putri", "isInhal": False},
                {"name": "Eka Lestari", "isInhal": False},
            ],
            "ipa": [
                {"name": "Bagas Pratama", "isInhal": False},
                {"name": "Gita Permata", "isInhal": False},
            ],
        }
    if "inhal_records" not in st.session_state:
        st.session_state["inhal_records"] = []
    if "inhal_search_result" not in st.session_state:
        st.session_state["inhal_search_result"] = None

    # Ambil daftar siswa dan program dari database jika tersedia
    student_names = ["Bagas Pratama", "Ahmad Farhan", "Dimas Aditya", "Alya Putri", "Citra Maharani", "Eka Lestari"]
    try:
        db_students = database.get_students()
        if db_students:
            student_names = [str(s["name"]) for s in db_students]
    except Exception:
        pass

    programs_list = ["Matematika SMP", "Calistung", "IPA Terpadu", "Persiapan UTBK", "Matematika SD"]
    try:
        db_progs = database.get_programs()
        if db_progs:
            programs_list = [str(p["name"]) for p in db_progs]
    except Exception:
        pass

    # TOP HEADER
    st.markdown("""
        <div class="top-header">
            <div>
                <h1 class="page-title">Kelompok Belajar & Konsultasi Jadwal Pengganti</h1>
                <p class="page-subtitle">Pencocokan ruangan dan jadwal bebas bentrok untuk siswa yang berhalangan hadir (inhal) serta manajemen kuota kelompok (maks. 5 siswa).</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CARD 1: FORM KONSULTASI SISWA & PENCOCOKAN JADWAL PENGGANTI (ANTI-BENTROK)
    with st.container(border=True):
        st.markdown('<div class="card-box-marker"></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 16px; font-weight: 700; color: #1e50bb;">
                    🔍 Konsultasi Jadwal & Ruang Pengganti (Siswa Inhal)
                </div>
                <span style="background-color: #eff6ff; color: #1d4ed8; font-weight: 600; border: 1px solid #bfdbfe; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                    🛡️ Sistem Anti-Bentrok & Cek Ruang
                </span>
            </div>
            <p style="font-size: 13.5px; color: #64748b; margin-bottom: 18px;">
                <strong>Studi Kasus:</strong> Siswa A tidak masuk hari <strong>Senin</strong> (misal sakit). Di hari <strong>Selasa</strong>, siswa & orang tua berkonsultasi ke admin untuk mencocokkan jadwal dan ruangan pengganti agar tidak ketinggalan materi dan <strong>tidak bentrok</strong> dengan kelas yang akan dimulai di hari Selasa.
            </p>
        """, unsafe_allow_html=True)

        with st.form("form_konsultasi_inhal"):
            c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
            with c1:
                sel_siswa = st.selectbox("Nama siswa", student_names, index=0 if "Bagas Pratama" in student_names else 0)
            with c2:
                sel_program = st.selectbox("Materi yang terlewat", programs_list, index=0 if "Matematika SMP" in programs_list else 0)
            with c3:
                sel_hari_asal = st.selectbox("Hari absen", ["Senin (Sakit)", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"], index=0)
            with c4:
                sel_hari_tujuan = st.selectbox("Cari jadwal di hari", ["Selasa (Hari Ini)", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"], index=0)

            btn_cek_ruang = st.form_submit_button("Cocokkan Ruang & Cek Bentrok", type="primary", use_container_width=True)

            if btn_cek_ruang:
                st.session_state["inhal_search_result"] = {
                    "siswa": sel_siswa,
                    "program": sel_program,
                    "hari_asal": sel_hari_asal.split()[0],
                    "hari_tujuan": sel_hari_tujuan.split()[0],
                }

        # TAMPILKAN HASIL PENCOCOKAN JIKA ADA PENCARIAN
        inhal_search = st.session_state.get("inhal_search_result")
        if inhal_search:
            st.markdown(f"""
                <div style="margin-top: 18px; padding-top: 14px; border-top: 1.5px solid #edf2f7;">
                    <div style="font-size: 14.5px; font-weight: 700; color: #1e293b; margin-bottom: 12px;">
                        🎯 Hasil Pengecekan Ruangan & Kelas di Hari <span style="color: #1e50bb;">{inhal_search['hari_tujuan']}</span> untuk Siswa <strong>{html.escape(inhal_search['siswa'])}</strong>:
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Hitung ketersediaan kelompok terkait
            prog_name = inhal_search["program"]
            target_key = "matematika"
            target_group_name = "Matematika SMP · Kelompok 1"
            ruang_name = "Ruang Alpha (Lt. 1)"
            jam_str = "15:30 – 17:00"
            tutor_name = "Kak Rina Wijaya"

            if "calistung" in prog_name.lower():
                target_key = "calistung"
                target_group_name = "Calistung · Kelompok 1"
                ruang_name = "Ruang Beta (Lt. 1)"
                tutor_name = "Kak Yoga Saputra"
            elif "ipa" in prog_name.lower():
                target_key = "ipa"
                target_group_name = "IPA Terpadu · Kelompok 1"
                ruang_name = "Ruang Alpha (Lt. 1)"
                jam_str = "17:15 – 18:45"
                tutor_name = "Kak Fajar Nugroho"

            current_mems = st.session_state["kelompok_state"].get(target_key, [])
            sisa_kursi = 5 - len(current_mems)

            # OPSI 1: KELAS PARALEL REGULER
            with st.container(border=True):
                col_info, col_act = st.columns([4, 1.8])
                with col_info:
                    if sisa_kursi > 0:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <strong style="font-size: 15px; color: #1e293b;">{target_group_name} ({inhal_search['hari_tujuan']})</strong>
                                <span style="background-color: #dcfce7; color: #15803d; font-size: 11.5px; font-weight: 700; padding: 2px 9px; border-radius: 9999px;">
                                    ✓ Aman · Tidak Bentrok
                                </span>
                            </div>
                            <div style="font-size: 13.5px; color: #64748b; margin-bottom: 4px;">
                                📍 <strong>{ruang_name}</strong> · ⏰ <strong>{jam_str}</strong> · 👨‍🏫 Tutor: <strong>{tutor_name}</strong>
                            </div>
                            <div style="font-size: 13px; color: #15803d;">
                                Ruangan dan tutor tidak bentrok dengan jadwal lain di hari {inhal_search['hari_tujuan']}. Sisa kuota: <strong>{sisa_kursi} kursi</strong> (muat untuk siswa inhal).
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <strong style="font-size: 15px; color: #1e293b;">{target_group_name}</strong>
                                <span style="background-color: #fee2e2; color: #dc2626; font-size: 11.5px; font-weight: 700; padding: 2px 9px; border-radius: 9999px;">
                                    ⚠️ Kuota Penuh (5/5)
                                </span>
                            </div>
                            <div style="font-size: 13.5px; color: #dc2626;">
                                Kelompok ini sudah penuh 5/5 siswa. Silakan pilih opsi ruang cadangan di bawah.
                            </div>
                        """, unsafe_allow_html=True)

                with col_act:
                    if sisa_kursi > 0:
                        if st.button("Daftarkan ke Kelas Ini", key="btn_daftar_inhal_1", type="primary", use_container_width=True):
                            # Masukkan ke kelompok
                            siswa_obj = {
                                "name": inhal_search["siswa"],
                                "isInhal": True,
                                "hariAsal": inhal_search["hari_asal"],
                                "hariTujuan": inhal_search["hari_tujuan"],
                                "ruang": ruang_name,
                            }
                            # Cek duplikat
                            already_in = any(m["name"].lower() == inhal_search["siswa"].lower() for m in current_mems)
                            if already_in:
                                st.warning(f"Siswa '{inhal_search['siswa']}' sudah terdaftar di kelompok ini.")
                            else:
                                current_mems.append(siswa_obj)
                                st.session_state["kelompok_state"][target_key] = current_mems
                                st.session_state["inhal_records"].insert(0, {
                                    "student": inhal_search["siswa"],
                                    "program": inhal_search["program"],
                                    "hariAsal": inhal_search["hari_asal"],
                                    "hariTujuan": inhal_search["hari_tujuan"],
                                    "jam": jam_str,
                                    "ruang": ruang_name,
                                    "tutor": tutor_name,
                                    "groupKey": target_key,
                                })
                                st.toast(f"✓ Siswa '{inhal_search['siswa']}' berhasil dijadwalkan ke {ruang_name} tanpa bentrok!", icon="🎉")
                                st.rerun()

            # OPSI 2: RUANG CADANGAN KOSONG
            with st.container(border=True):
                col_info2, col_act2 = st.columns([4, 1.8])
                with col_info2:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <strong style="font-size: 15px; color: #1e293b;">Sesi Inhal Mandiri di Ruang Beta</strong>
                            <span style="background-color: #dcfce7; color: #15803d; font-size: 11.5px; font-weight: 700; padding: 2px 9px; border-radius: 9999px;">
                                ✓ Ruang Kosong · Aman
                            </span>
                        </div>
                        <div style="font-size: 13.5px; color: #64748b; margin-bottom: 4px;">
                            📍 <strong>Ruang Beta (Lt. 1)</strong> · ⏰ <strong>17:15 – 18:45</strong> · 👨‍🏫 Tutor: <strong>Kak Budi Santoso</strong>
                        </div>
                        <div style="font-size: 13px; color: #1e50bb;">
                            Ruang Beta tidak digunakan di jam ini pada hari {inhal_search['hari_tujuan']}. Sangat cocok untuk sesi inhal privat bebas bentrok.
                        </div>
                    """, unsafe_allow_html=True)
                with col_act2:
                    if st.button("Buka Sesi Ruang Beta", key="btn_daftar_inhal_2", use_container_width=True):
                        cal_mems = st.session_state["kelompok_state"].get("calistung", [])
                        if len(cal_mems) < 5:
                            cal_mems.append({
                                "name": inhal_search["siswa"],
                                "isInhal": True,
                                "hariAsal": inhal_search["hari_asal"],
                                "hariTujuan": inhal_search["hari_tujuan"],
                                "ruang": "Ruang Beta (Lt. 1)",
                            })
                            st.session_state["kelompok_state"]["calistung"] = cal_mems
                            st.session_state["inhal_records"].insert(0, {
                                "student": inhal_search["siswa"],
                                "program": inhal_search["program"],
                                "hariAsal": inhal_search["hari_asal"],
                                "hariTujuan": inhal_search["hari_tujuan"],
                                "jam": "17:15 – 18:45",
                                "ruang": "Ruang Beta (Lt. 1)",
                                "tutor": "Kak Budi Santoso",
                                "groupKey": "calistung",
                            })
                            st.toast(f"✓ Sesi inhal di Ruang Beta untuk '{inhal_search['siswa']}' berhasil dijadwalkan!", icon="🎉")
                            st.rerun()

            # OPSI 3: SIMULASI BENTROK JADWAL
            with st.container(border=True):
                col_info3, col_act3 = st.columns([4, 1.8])
                with col_info3:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                            <strong style="font-size: 15px; color: #94a3b8;">Ruang Alpha (Sesi Sore)</strong>
                            <span style="background-color: #fee2e2; color: #b91c1c; font-size: 11.5px; font-weight: 700; padding: 2px 9px; border-radius: 9999px;">
                                ✗ Bentrok Ruangan
                            </span>
                        </div>
                        <div style="font-size: 13.5px; color: #dc2626;">
                            JADWAL BENTROK: Ruang Alpha di jam 17:15–18:45 sudah digunakan oleh kelas reguler lain. Sistem melarang penempatan di jam ini.
                        </div>
                    """, unsafe_allow_html=True)
                with col_act3:
                    st.button("Tidak Tersedia", key="btn_daftar_inhal_3", disabled=True, use_container_width=True)

    # CARD 2: FORM TAMBAH SISWA REGULER KE KELOMPOK
    with st.form("form_add_reguler_member", clear_on_submit=True):
        st.markdown('<div class="card-heading">Tambah siswa ke kelompok reguler</div>', unsafe_allow_html=True)
        col_grp, col_std, col_btn = st.columns([5, 5, 2])
        with col_grp:
            sel_target_grp = st.selectbox(
                "Pilih kelompok",
                [
                    ("matematika", "Matematika SMP · Kelompok 1 (Kak Rina Wijaya)"),
                    ("calistung", "Calistung · Kelompok 1 (Kak Yoga Saputra)"),
                    ("ipa", "IPA Terpadu · Kelompok 1 (Kak Fajar Nugroho)"),
                ],
                format_func=lambda x: x[1],
            )
        with col_std:
            reg_siswa_name = st.selectbox("Pilih siswa", student_names, key="sel_reg_siswa")
        with col_btn:
            btn_tambah_reg = st.form_submit_button("Tambahkan", type="primary", use_container_width=True)

        if btn_tambah_reg:
            grp_key = sel_target_grp[0]
            current_grp_list = st.session_state["kelompok_state"].get(grp_key, [])
            if len(current_grp_list) >= 5:
                st.error(f"❌ Sistem Menolak: Kelompok {sel_target_grp[1]} sudah penuh (5/5 siswa). Sesuai aturan, anggota ke-6 tidak dapat ditambahkan!")
            elif any(m["name"].lower() == reg_siswa_name.lower() for m in current_grp_list):
                st.warning(f"Siswa '{reg_siswa_name}' sudah terdaftar di kelompok ini!")
            else:
                current_grp_list.append({"name": reg_siswa_name, "isInhal": False})
                st.session_state["kelompok_state"][grp_key] = current_grp_list
                st.toast(f"✓ Siswa '{reg_siswa_name}' berhasil ditambahkan ke kelompok reguler!", icon="🎉")
                st.rerun()

    # CARD 3: GRID KARTU KELOMPOK BELAJAR (KUOTA MAKSIMAL 5 SISWA)
    col_k1, col_k2, col_k3 = st.columns(3)
    group_configs = [
        (col_k1, "matematika", "Matematika SMP · Kelompok 1", "Kak Rina Wijaya", "Ruang Alpha (Lt. 1)"),
        (col_k2, "calistung", "Calistung · Kelompok 1", "Kak Yoga Saputra", "Ruang Beta (Lt. 1)"),
        (col_k3, "ipa", "IPA Terpadu · Kelompok 1", "Kak Fajar Nugroho", "Ruang Alpha (Lt. 1)"),
    ]

    for col, key, title, tutor, room in group_configs:
        with col:
            with st.container(border=True):
                mems = st.session_state["kelompok_state"].get(key, [])
                count = len(mems)
                badge_style = "background-color: #fee2e2; color: #dc2626;" if count >= 5 else "background-color: #e0f2fe; color: #0284c7;"
                badge_text = "5/5 (Penuh)" if count >= 5 else f"{count}/5"

                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div>
                            <div style="font-weight: 700; font-size: 15.5px; color: #1e293b;">{title}</div>
                            <div style="font-size: 12.5px; color: #64748b; margin-top: 2px;">
                                👨‍🏫 {tutor}<br>📍 {room}
                            </div>
                        </div>
                        <span style="{badge_style} border-radius: 9999px; font-weight: 700; padding: 3px 10px; font-size: 12px;">
                            {badge_text}
                        </span>
                    </div>
                    <div style="border-top: 1px solid #f1f5f9; padding-top: 8px; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #8292a8; letter-spacing: 0.5px;">
                        ANGGOTA SISWA
                    </div>
                """, unsafe_allow_html=True)

                if not mems:
                    st.markdown("<p style='color: #94a3b8; font-size: 13px; text-align: center; margin: 16px 0;'>Belum ada anggota.</p>", unsafe_allow_html=True)
                else:
                    for idx, m in enumerate(mems):
                        c_name, c_del = st.columns([3.8, 1.4])
                        with c_name:
                            inhal_tag = f'<span class="badge-inhal-st">Inhal: Ganti {m.get("hariAsal", "Senin")}</span>' if m.get("isInhal") else ""
                            st.markdown(f'<div style="font-size: 13.5px; font-weight: 500; color: #1e293b; padding-top: 4px;">{html.escape(m["name"])}{inhal_tag}</div>', unsafe_allow_html=True)
                        with c_del:
                            if st.button("Keluarkan", key=f"btn_rem_{key}_{idx}", type="secondary"):
                                removed_name = m["name"]
                                mems.pop(idx)
                                st.session_state["kelompok_state"][key] = mems
                                # Hapus juga dari inhal records jika ada
                                st.session_state["inhal_records"] = [
                                    r for r in st.session_state["inhal_records"]
                                    if not (r["student"] == removed_name and r.get("groupKey") == key)
                                ]
                                st.toast(f"✓ Siswa '{removed_name}' dikeluarkan dari kelompok.")
                                st.rerun()

    # CARD 4: TABEL RIWAYAT PENJADWALAN KELAS PENGGANTI (INHAL) AKTIF
    with st.container(border=True):
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <span style="font-weight: 700; font-size: 15px; color: #1e293b;">📋 Daftar Siswa Mengikuti Kelas Pengganti (Inhal)</span>
                    <p style="font-size: 13px; color: #64748b; margin: 2px 0 0 0;">Catatan resmi bagi siswa yang absen dan telah ditempatkan pada kelas pengganti bebas bentrok.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        inhal_recs = st.session_state.get("inhal_records", [])
        if not inhal_recs:
            st.markdown(
                "<p style='text-align: center; color: #64748b; padding: 24px 20px; margin: 0; font-size: 13.5px;'>"
                "Belum ada siswa yang dijadwalkan kelas pengganti. Gunakan form konsultasi di atas untuk mencocokkan jadwal.</p>",
                unsafe_allow_html=True,
            )
        else:
            # Header Tabel Inhal
            st.markdown('<div class="table-card-marker"></div>', unsafe_allow_html=True)
            th1, th2, th3, th4, th5, th6 = st.columns([2.5, 2.0, 1.6, 2.3, 2.2, 1.4])
            with th1:
                st.markdown('<div class="table-th table-header-marker">SISWA</div>', unsafe_allow_html=True)
            with th2:
                st.markdown('<div class="table-th">MATERI</div>', unsafe_allow_html=True)
            with th3:
                st.markdown('<div class="table-th">HARI ABSEN</div>', unsafe_allow_html=True)
            with th4:
                st.markdown('<div class="table-th">JADWAL PENGGANTI</div>', unsafe_allow_html=True)
            with th5:
                st.markdown('<div class="table-th">RUANG & TUTOR</div>', unsafe_allow_html=True)
            with th6:
                st.markdown('<div class="table-th"></div>', unsafe_allow_html=True)

            for i, r in enumerate(inhal_recs):
                r1, r2, r3, r4, r5, r6 = st.columns([2.5, 2.0, 1.6, 2.3, 2.2, 1.4])
                with r1:
                    st.markdown(f'<div class="program-name-cell">{html.escape(r["student"])}</div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<span class="badge-level">{html.escape(r["program"])}</span>', unsafe_allow_html=True)
                with r3:
                    st.markdown(f'<div class="table-text-cell" style="color: #dc2626; font-weight: 600;">{html.escape(r["hariAsal"])}</div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div class="table-text-cell"><strong>{html.escape(r["hariTujuan"])}</strong> · {html.escape(r["jam"])}</div>', unsafe_allow_html=True)
                with r5:
                    st.markdown(f'<div class="table-text-cell">{html.escape(r["ruang"])}<br><small style="color:#64748b;">{html.escape(r["tutor"])}</small></div>', unsafe_allow_html=True)
                with r6:
                    if st.button("Batalkan", key=f"btn_canc_inhal_{i}", type="secondary"):
                        # Hapus dari kelompok
                        g_key = r.get("groupKey")
                        if g_key and g_key in st.session_state["kelompok_state"]:
                            st.session_state["kelompok_state"][g_key] = [
                                m for m in st.session_state["kelompok_state"][g_key]
                                if m["name"] != r["student"]
                            ]
                        inhal_recs.pop(i)
                        st.session_state["inhal_records"] = inhal_recs
                        st.toast(f"✓ Jadwal inhal untuk '{r['student']}' dibatalkan.")
                        st.rerun()


# =============================================================================
# 4. MENU LAINNYA: TAMPILKAN FILE HTML DARI FOLDER PUBLIC/
# =============================================================================
else:
    file_map = {
        "Dashboard": "dashboard.html",
    }

    target_file = file_map.get(menu, "dashboard.html")
    file_path = os.path.join(PUBLIC_DIR, target_file)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        # Sisipkan CSS asli + reset margin-left sidebar agar pas di area konten Streamlit
        css_path = os.path.join(PUBLIC_DIR, 'css', 'style.css')
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as cf:
                extra_override = "\n.main-wrapper { margin-left: 0 !important; padding: 4px !important; }\n"
                raw_html = raw_html.replace(
                    '<link rel="stylesheet" href="css/style.css">',
                    f'<style>\n{cf.read()}{extra_override}\n</style>'
                )

        components.html(raw_html, height=1100, scrolling=True)
    else:
        st.warning(f"File {target_file} belum ditemukan di folder public/.")
