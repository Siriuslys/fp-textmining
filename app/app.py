"""
Topic Modeling Berita Online Multi-Portal Indonesia
Dashboard: Ringkasan S1 | Jelajah Topik | Tuning S2 | Embedding S3

Jalankan lokal (dari folder tempat app.py berada):
    streamlit run app.py

Struktur data yang dibutuhkan (lihat utils/data_loader.py untuk detail path):
    output/topic_labels.csv
    output/topic_model_comparison_s1.csv
    hasil_optuna_hyperparameter.csv      (di root repo)
    output/s3/s3_embedding_comparison.csv
    output/fig*.png, output/s3/fig_*.png (opsional)
"""

import streamlit as st

st.set_page_config(
    page_title="Topic Modeling — Berita Indonesia",
    page_icon="\U0001F4F0",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import inject_css, kicker
from utils.data_loader import (
    load_topic_labels, load_s1_comparison, load_s2_results, load_s3_comparison,
    debug_paths,
)
from tabs import overview_s1, explore_topics, tuning_s2, embedding_s3


inject_css()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### \U0001F4F0 Ruang Topik")
    st.caption("Final project text mining — analisis topik berita Indonesia")

    st.markdown("---")
    st.markdown("**Korpus**")
    st.markdown(
        "- 20.334 artikel\n"
        "- 6 portal berita\n"
        "- 8 kategori\n"
        "- Periode scraping Mei–Jun 2026"
    )

    st.markdown("---")
    st.markdown("**Susunan redaksi**")
    st.markdown(
        "1. Audrey Sasia Wijaya\n"
        "2. Lathifah Sahda\n"
        "3. Mufrih Fakhir"
    )

    with st.expander("Diagnostik path data"):
        st.json(debug_paths())

# ── Masthead ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="masthead">
        <div>
            <h1 style="margin-bottom:0;">Ruang Topik</h1>
        </div>
        <div class="masthead-date">LDA · NMF · BERTOPIC</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Pemetaan topik 20.334 artikel dari enam portal berita Indonesia — "
    "Detik, Kompas, Tribun, CNN Indonesia, Antara, dan Liputan6."
)

# ── Load data once (cached) ─────────────────────────────────────────
df_labels = load_topic_labels()
df_s1 = load_s1_comparison()
df_s2 = load_s2_results()
df_s3 = load_s3_comparison()

# ── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Home",
    "Jelajah topik",
    "Tuning BERTopic",
    "Model embedding",
])

with tab1:
    overview_s1.render(df_labels, df_s1)

with tab2:
    explore_topics.render(df_labels)

with tab3:
    tuning_s2.render(df_s2)

with tab4:
    embedding_s3.render(df_s3)
