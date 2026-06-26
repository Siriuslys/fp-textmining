"""
Ringkasan — Skenario S1.
Perbandingan LDA, NMF, BERTopic (konfigurasi awal) pada korpus 20.334 artikel.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import static_figure_path
from utils.theme import kicker, rule, KATEGORI_COLORS, MODEL_COLORS
from utils import compat as ui


def _plotly_layout(fig: go.Figure, height: int = 380, title: str | None = None, showlegend: bool = False) -> go.Figure:
    """Layout konsisten ala cetak — tanpa gridlines tebal, font monospace untuk sumbu."""
    fig.update_layout(
        height=height + (40 if showlegend else 0),
        title=dict(text=title, font=dict(family="Source Serif 4, Georgia, serif", size=16)) if title else None,
        font=dict(family="JetBrains Mono, monospace", size=11, color="#1F1B16"),
        plot_bgcolor="#FAF7F0",
        paper_bgcolor="#FAF7F0",
        margin=dict(l=10, r=10, t=50 if title else 10, b=50 if showlegend else 10),
        showlegend=showlegend,
        legend=dict(
            orientation="h", yanchor="top", y=-0.18, x=0,
            bgcolor="rgba(0,0,0,0)",
        ) if showlegend else None,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#D9D2C4")
    fig.update_yaxes(showgrid=True, gridcolor="#EFE9DB", zeroline=False)
    return fig


def render(df_labels: pd.DataFrame | None, df_s1: pd.DataFrame | None) -> None:
    if df_labels is None:
        st.error(
            "`output/topic_labels.csv` belum ditemukan. Cek panel "
            "**Diagnostik path data** di sidebar untuk melihat lokasi yang dicari."
        )
        return

    # ── Lead numbers ───────────────────────────────────────────────
    kicker("Korpus")
    st.markdown("#### Apa yang diolah")

    n_outlier = int(df_labels["bertopic_outlier"].sum()) if "bertopic_outlier" in df_labels else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Artikel", f"{len(df_labels):,}")
    c2.metric("Portal", df_labels["portal"].nunique())
    c3.metric("Kategori", df_labels["kategori"].nunique())
    c4.metric("Outlier BERTopic", f"{n_outlier / len(df_labels):.1%}")

    c1, c2 = st.columns(2)
    with c1:
        portal_counts = df_labels["portal"].value_counts().sort_values(ascending=True)
        fig = go.Figure(go.Bar(
            x=portal_counts.values, y=portal_counts.index, orientation="h",
            marker_color="#9C6B30", text=portal_counts.values, textposition="outside",
        ))
        _plotly_layout(fig, height=260, title="Artikel per portal")
        ui.plotly_chart(fig)

    with c2:
        kat_counts = df_labels["kategori"].value_counts().sort_values(ascending=True)
        colors = [KATEGORI_COLORS.get(k, "#6B6258") for k in kat_counts.index]
        fig = go.Figure(go.Bar(
            x=kat_counts.values, y=kat_counts.index, orientation="h",
            marker_color=colors, text=kat_counts.values, textposition="outside",
        ))
        _plotly_layout(fig, height=260, title="Artikel per kategori")
        ui.plotly_chart(fig)

    rule()

    # ── Model comparison ─────────────────────────────────────────────
    kicker("Skenario 1")
    st.markdown("#### LDA, NMF, dan BERTopic berhadapan")
    st.caption(
        "Coherence Score (C\u1d65) pada beberapa nilai k untuk LDA dan NMF; "
        "BERTopic dijalankan dengan target k = 25 topik."
    )

    if df_s1 is None:
        st.info("`output/topic_model_comparison_s1.csv` belum ditemukan — grafik dilewati.")
    else:
        c1, c2 = st.columns([3, 2])

        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_s1["k"], y=df_s1["LDA C_v"], mode="lines+markers",
                name="LDA", line=dict(color=MODEL_COLORS["LDA"], width=2),
                marker=dict(size=7),
            ))
            fig.add_trace(go.Scatter(
                x=df_s1["k"], y=df_s1["NMF C_v"], mode="lines+markers",
                name="NMF", line=dict(color=MODEL_COLORS["NMF"], width=2),
                marker=dict(size=7),
            ))
            bert_col = "BERTopic C_v"
            if bert_col in df_s1.columns:
                bert_rows = df_s1[df_s1[bert_col].astype(str) != "-"]
                if not bert_rows.empty:
                    fig.add_trace(go.Scatter(
                        x=bert_rows["k"], y=bert_rows[bert_col].astype(float),
                        mode="markers", name="BERTopic (auto)",
                        marker=dict(size=14, symbol="star", color=MODEL_COLORS["BERTopic"]),
                    ))
            _plotly_layout(fig, height=380, title="Coherence Cᵥ menurut jumlah topik (k)", showlegend=True)
            fig.update_xaxes(title="k")
            fig.update_yaxes(title="Cᵥ")
            ui.plotly_chart(fig)

        with c2:
            st.markdown("**Ringkasan metrik S1 — k = 25**")
            df_summary = pd.DataFrame({
                "Model": ["NMF ★", "BERTopic", "LDA"],
                "Cᵥ": [0.8250, 0.7780, 0.6162],
                "Silhouette": [0.6393, 0.1121, 0.5442],
                "Topic Div.": [0.9400, 0.9263, 0.8520],
                "Outlier": ["–", "27,2%", "–"],
            })
            ui.df(df_summary, hide_index=True)
            st.markdown("**Tabel lengkap**")
            ui.df(df_s1, hide_index=True, height=230)

        st.markdown(
            "> NMF (k=25) menghasilkan topik paling koheren secara kuantitatif. "
            "BERTopic unggul secara kualitatif — mampu mendeteksi dokumen outlier "
            "dan menentukan jumlah topik tanpa ditentukan terlebih dahulu."
        )

    rule()

    # ── Static figures ───────────────────────────────────────────────
    kicker("Arsip visual")
    st.markdown("#### Plot pendukung dari notebook")

    fig_files = {
        "Coherence LDA per k": "fig01_lda_coherence.png",
        "Coherence NMF per k": "fig04_nmf_coherence.png",
        "Perbandingan tiga model": "fig09_s1_comparison.png",
        "Kesamaan antar topik": "fig11_similarity_heatmap.png",
    }
    cols = st.columns(2)
    shown = 0
    for caption, fname in fig_files.items():
        path = static_figure_path(fname)
        if path:
            with cols[shown % 2]:
                ui.image(path, caption=caption)
            shown += 1

    if shown == 0:
        st.caption("Belum ada plot statis di `output/` — lewati bagian ini.")
