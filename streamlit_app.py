import html
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
        margin: 0 0 6px 0;
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
    div[data-testid="stForm"] div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
        height: 44px !important;
        min-height: 44px !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
    }

    div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }

    div[data-testid="stForm"] div[data-baseweb="base-input"] {
        background-color: transparent !important;
        border: none !important;
    }

    div[data-testid="stForm"] div[data-baseweb="input"] input {
        background-color: transparent !important;
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
    }

    .badge-level.badge-smp {
        background-color: #ebf4ff;
        color: #3182ce;
    }

    .badge-level.badge-sma {
        background-color: #e6f6ff;
        color: #0284c7;
    }

    .session-count {
        font-size: 14px;
        color: #334155;
        font-weight: 500;
        line-height: 1.5;
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

    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[kind="secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="baseButton-secondary"]:hover p,
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .table-card-marker) button[data-testid="stBaseButton-secondary"]:hover p {
        color: #b91c1c !important;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

MENU_ITEMS = [
    "Dashboard",
    "Siswa dan Wali",
    "Program",
    "Tutor",
    "Ruang Belajar",
    "Kelompok Belajar",
    "Jadwal",
    "Tagihan",
    "Pembayaran",
]

if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Program"


# =============================================================================
# 2. SIDEBAR DEEP NAVY (PERSIS PUBLIC/JS/SIDEBAR.JS)
# =============================================================================
with st.sidebar:
    st.markdown("""
        <div class="brand-container">
            <div class="brand-title">
                Optimatika <span class="brand-sub">· Admin</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for item in MENU_ITEMS:
        is_active = (st.session_state.active_menu == item)
        if st.button(
            item,
            key=f"nav_{item}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_menu = item
            st.rerun()

    st.markdown('<div class="sidebar-footer-divider"></div>', unsafe_allow_html=True)
    if st.button("Keluar", key="btn_logout", type="secondary", use_container_width=True):
        st.session_state.active_menu = "Dashboard"
        st.toast("Anda telah keluar dari sesi Admin Optimatika.")

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

    # CARD 1: FORM TAMBAH PROGRAM (SATU CARD UTUH)
    with st.form("form_add_program", clear_on_submit=True):
        st.markdown('<div class="card-heading">Tambah program</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nama_input = st.text_input("Nama program", placeholder="contoh: Matematika Dasar")
        with col2:
            jenjang_input = st.selectbox("Jenjang", ["SD", "SMP", "SMA"])
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
        th1, th2, th3, th4 = st.columns([4.5, 2.5, 1.8, 1.2])
        with th1:
            st.markdown('<div class="table-th table-header-marker">PROGRAM</div>', unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="table-th">JENJANG</div>', unsafe_allow_html=True)
        with th3:
            st.markdown('<div class="table-th">PERTEMUAN / BULAN</div>', unsafe_allow_html=True)
        with th4:
            st.markdown('<div class="table-th"></div>', unsafe_allow_html=True)

        # Baris Data Program dari Neon PostgreSQL
        try:
            programs = database.get_programs()
            if not programs:
                st.markdown(
                    "<p style='text-align: center; color: #64748b; padding: 28px 20px; margin: 0;'>"
                    "Belum ada data program di database Neon.</p>",
                    unsafe_allow_html=True,
                )
            else:
                for p in programs:
                    r1, r2, r3, r4 = st.columns([4.5, 2.5, 1.8, 1.2])
                    with r1:
                        safe_name = html.escape(str(p['name']))
                        st.markdown(f'<div class="program-name-cell">{safe_name}</div>', unsafe_allow_html=True)
                    with r2:
                        lvl = str(p['level']).upper()
                        badge_class = "badge-level"
                        if lvl == "SMP":
                            badge_class += " badge-smp"
                        elif lvl == "SMA":
                            badge_class += " badge-sma"
                        st.markdown(f'<span class="{badge_class}">{html.escape(lvl)}</span>', unsafe_allow_html=True)
                    with r3:
                        st.markdown(
                            f'<span class="session-count">{int(p["sessions_per_month"])}×</span>',
                            unsafe_allow_html=True,
                        )
                    with r4:
                        if st.button("Hapus", key=f"btn_del_{p['id']}", type="secondary"):
                            try:
                                database.delete_program(p['id'])
                                try:
                                    database.sync_ke_html()
                                except Exception:
                                    pass
                                st.toast(f"✓ Program '{p['name']}' berhasil dihapus dari Neon!", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Gagal menghapus: {e}")

        except Exception as e:
            st.error(f"Gagal mengambil data dari database Neon: {e}")


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
