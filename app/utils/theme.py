"""
Tema visual kustom — identitas "ruang redaksi data" (data newsroom).

Subjek aplikasi ini adalah analisis topik berita, sehingga elemen
visualnya meminjam dari dunia percetakan koran: rule tipis, kop
section bergaya masthead, label kategori seperti rubrik koran,
dan tipografi serif untuk judul + monospace untuk angka/metrik.

Palet:
  - Kertas    #FAF7F0  (background utama)
  - Tinta     #1F1B16  (teks utama)
  - Tinta pudar #6B6258 (teks sekunder)
  - Aksen ekonomi/politik dst dipetakan per kategori (lihat KATEGORI_COLORS)
  - Garis     #D9D2C4  (rule/border)

Tipografi:
  - Headline : "Source Serif 4" (serif editorial, bukan default Times)
  - Body     : font default Streamlit (sans, untuk keterbacaan UI)
  - Data     : "JetBrains Mono" (angka, kode, label model)
"""

import streamlit as st

# Warna per kategori berita -- dipakai konsisten di semua tab
# supaya "ekonomi" misalnya selalu warna yang sama di chart manapun.
KATEGORI_COLORS = {
    "ekonomi": "#9C6B30",     # ochre - kertas koran lama
    "politik": "#8B3A3A",     # merah bata
    "olahraga": "#3A6B4C",    # hijau lapangan
    "hiburan": "#7A4F8C",     # ungu spotlight
    "otomotif": "#3A5A7A",    # biru baja
    "teknologi": "#3A7A7A",   # teal sirkuit
    "sains": "#5A6B3A",       # hijau lab
    "lifestyle": "#B5572A",   # terracotta
}

MODEL_COLORS = {
    "LDA": "#6B6258",
    "NMF": "#9C6B30",
    "BERTopic": "#8B3A3A",
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {
            --paper: #FAF7F0;
            --ink: #1F1B16;
            --ink-faded: #6B6258;
            --rule: #D9D2C4;
            --accent: #8B3A3A;
        }

        /* Latar halaman bertekstur kertas */
        .stApp {
            background-color: var(--paper);
        }

        /* Headline editorial */
        h1, h2, h3 {
            font-family: 'Source Serif 4', Georgia, serif !important;
            color: var(--ink) !important;
            letter-spacing: -0.01em;
        }

        h1 {
            font-weight: 700 !important;
            border-bottom: 3px solid var(--ink);
            padding-bottom: 0.4rem;
        }

        h2 {
            font-weight: 600 !important;
            border-top: 1px solid var(--rule);
            padding-top: 1rem;
            margin-top: 0.5rem !important;
        }

        /* Eyebrow / kicker label di atas judul */
        .kicker {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--accent);
            font-weight: 700;
            margin-bottom: -0.4rem;
        }

        /* Metric: angka jadi monospace, label jadi kicker style */
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            color: var(--ink) !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--ink-faded) !important;
        }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--rule);
            border-radius: 2px;
            padding: 0.9rem 1rem 0.7rem;
        }

        /* Tab bar -- meniru navigasi rubrik koran */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid var(--ink);
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 500;
            color: var(--ink-faded);
            padding: 10px 18px;
        }
        .stTabs [aria-selected="true"] {
            color: var(--ink) !important;
            background: var(--paper) !important;
            font-weight: 700 !important;
        }

        /* Sidebar -- kolom "edisi" */
        section[data-testid="stSidebar"] {
            background-color: #F1ECE0;
            border-right: 1px solid var(--rule);
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2 {
            border: none !important;
            padding: 0 !important;
        }

        /* Tabel & dataframe */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--rule);
        }

        /* Caption */
        .stCaption, [data-testid="stCaptionContainer"] {
            color: var(--ink-faded) !important;
        }

        /* Rule pemisah custom */
        .section-rule {
            border: none;
            border-top: 1px solid var(--rule);
            margin: 1.2rem 0;
        }

        /* Pill kategori */
        .pill {
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 2px;
            border: 1px solid currentColor;
            margin-right: 4px;
        }

        /* Masthead */
        .masthead {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 3px double var(--ink);
            padding-bottom: 0.5rem;
            margin-bottom: 0.3rem;
        }
        .masthead-date {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--ink-faded);
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kicker(text: str) -> None:
    """Label kecil ala 'rubrik' di atas judul section."""
    st.markdown(f'<p class="kicker">{text}</p>', unsafe_allow_html=True)


def rule() -> None:
    st.markdown('<hr class="section-rule" />', unsafe_allow_html=True)


def category_pill(name: str) -> str:
    color = KATEGORI_COLORS.get(name.lower(), "#6B6258")
    return f'<span class="pill" style="color:{color}">{name}</span>'
