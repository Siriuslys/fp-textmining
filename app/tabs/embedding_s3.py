"""
Model embedding — Skenario S3.

Lima model sentence embedding dibandingkan sebagai input BERTopic,
dievaluasi pada target k = 15 topik.
File sumber: output/s3/s3_embedding_comparison.csv

Nama kolom coherence pada file ini bisa bervariasi tergantung versi
notebook (coherence_cv, coherence_C_v, C_v, Cv, dst), sehingga kolom
dicari secara fleksibel -- sama seperti pendekatan di tuning_s2.py.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import static_figure_path
from utils.theme import kicker, rule
from utils import compat as ui


PALETTE = ["#9C6B30", "#8B3A3A", "#3A6B4C", "#3A5A7A", "#7A4F8C"]


def _find_col(df: pd.DataFrame, *keywords: str) -> str | None:
    """Cari kolom yang namanya (lowercase) mengandung semua keyword."""
    for c in df.columns:
        cl = c.lower()
        if all(k in cl for k in keywords):
            return c
    return None


def render(df_s3: pd.DataFrame | None) -> None:
    kicker("Skenario 3")
    st.markdown("#### Lima model embedding berhadapan")
    st.caption(
        "Setiap model sentence embedding diuji sebagai input BERTopic dengan "
        "target k = 15 topik, lalu dinilai dari Coherence Cᵥ dan proporsi outlier."
    )

    if df_s3 is None:
        st.warning(
            "`output/s3/s3_embedding_comparison.csv` belum ditemukan. "
            "Cek panel **Diagnostik path data** di sidebar untuk lokasi yang dicari."
        )
        return

    coherence_col = _find_col(df_s3, "coher")
    if coherence_col is None:
        st.error(
            "Tidak menemukan kolom coherence pada `s3_embedding_comparison.csv`. "
            "Kolom yang tersedia: " + ", ".join(df_s3.columns)
        )
        ui.df(df_s3, hide_index=True)
        return

    model_col = _find_col(df_s3, "model") or df_s3.columns[0]
    embedding_col = _find_col(df_s3, "embedding")
    n_topics_col = _find_col(df_s3, "n_topic", "final") or _find_col(df_s3, "n_topic")
    noise_col = _find_col(df_s3, "noise") or _find_col(df_s3, "outlier")

    df_sorted = df_s3.sort_values(coherence_col, ascending=False).reset_index(drop=True)
    best = df_sorted.iloc[0]

    cols = st.columns(4)
    cols[0].metric("Model terbaik", best.get(model_col, "-"))
    cols[1].metric("Cᵥ terbaik", f"{best[coherence_col]:.4f}")
    if n_topics_col:
        cols[2].metric("Topik final", int(best[n_topics_col]))
    if noise_col:
        val = best[noise_col]
        pct = val * 100 if val <= 1 else val
        cols[3].metric("Outlier", f"{pct:.1f}%")

    rule()

    # ── Bar charts side by side ───────────────────────────────────────
    kicker("Perbandingan")
    st.markdown("#### Coherence dan outlier per model")

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=df_sorted[model_col], y=df_sorted[coherence_col],
            marker_color=PALETTE[:len(df_sorted)],
            text=df_sorted[coherence_col].map(lambda v: f"{v:.4f}"),
            textposition="outside",
        ))
        fig.update_layout(
            height=360,
            font=dict(family="JetBrains Mono, monospace", size=11, color="#1F1B16"),
            plot_bgcolor="#FAF7F0", paper_bgcolor="#FAF7F0",
            margin=dict(l=10, r=10, t=30, b=10),
            title=dict(text="Coherence Cᵥ", font=dict(family="Source Serif 4, serif", size=14)),
            showlegend=False,
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#EFE9DB")
        ui.plotly_chart(fig)

    with c2:
        if noise_col:
            noise_vals = df_sorted[noise_col]
            if noise_vals.max() <= 1:
                noise_vals = noise_vals * 100
            fig2 = go.Figure(go.Bar(
                x=df_sorted[model_col], y=noise_vals,
                marker_color=PALETTE[:len(df_sorted)],
                text=noise_vals.map(lambda v: f"{v:.1f}%"),
                textposition="outside",
            ))
            fig2.update_layout(
                height=360,
                font=dict(family="JetBrains Mono, monospace", size=11, color="#1F1B16"),
                plot_bgcolor="#FAF7F0", paper_bgcolor="#FAF7F0",
                margin=dict(l=10, r=10, t=30, b=10),
                title=dict(text="Outlier (noise) %", font=dict(family="Source Serif 4, serif", size=14)),
                showlegend=False,
            )
            fig2.update_xaxes(showgrid=False)
            fig2.update_yaxes(showgrid=True, gridcolor="#EFE9DB")
            ui.plotly_chart(fig2)
        else:
            st.caption("Kolom outlier/noise tidak ditemukan.")

    st.markdown("**Tabel lengkap**")
    ui.df(df_sorted, hide_index=True)

    embedding_name = f" ({best[embedding_col]})" if embedding_col else ""
    st.markdown(
        f"> **{best.get(model_col, '-')}**{embedding_name} memberikan "
        f"coherence tertinggi (Cᵥ = {best[coherence_col]:.4f}) di antara model embedding "
        "yang diuji, menjadikannya kandidat representasi terbaik untuk BERTopic pada korpus ini."
    )

    rule()

    # ── Static figures ───────────────────────────────────────────────
    kicker("Arsip visual")
    st.markdown("#### Plot pendukung")

    s3_figs = {
        "Perbandingan model embedding": "fig_s3_embedding_comparison.png",
        "Heatmap topik — model terbaik": "fig_s3_heatmap_best.png",
        "Word cloud — model terbaik": "fig_s3_wordcloud_best.png",
    }
    cols = st.columns(3)
    shown = 0
    for caption, fname in s3_figs.items():
        path = static_figure_path(fname, subdir="s3")
        if path:
            with cols[shown % 3]:
                ui.image(path, caption=caption)
            shown += 1

    if shown == 0:
        st.caption("Belum ada plot statis di `output/s3/`.")
