"""
Jelajah topik & artikel.

Filter portal/kategori, pilih model (LDA/NMF/BERTopic), telusuri topik
dan cari artikel berdasarkan judul.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.topic_labels import MODEL_DISPLAY_NAMES, label_for
from utils.data_loader import static_figure_path
from utils.theme import kicker, rule, KATEGORI_COLORS, MODEL_COLORS
from utils import compat as ui


def render(df_labels: pd.DataFrame | None) -> None:
    if df_labels is None:
        st.error(
            "`output/topic_labels.csv` belum ditemukan. Cek panel "
            "**Diagnostik path data** di sidebar."
        )
        return

    # ── Filter bar ───────────────────────────────────────────────────
    kicker("Saring")
    f1, f2, f3 = st.columns([1, 1, 1.4])

    with f1:
        portals = ["Semua portal"] + sorted(df_labels["portal"].unique().tolist())
        portal_sel = st.selectbox("Portal", portals, label_visibility="visible")

    with f2:
        kategoris = ["Semua kategori"] + sorted(df_labels["kategori"].unique().tolist())
        kategori_sel = st.selectbox("Kategori", kategoris)

    with f3:
        model_col = st.selectbox(
            "Model",
            options=list(MODEL_DISPLAY_NAMES.keys()),
            format_func=lambda c: MODEL_DISPLAY_NAMES[c],
        )

    df_filtered = df_labels.copy()
    if portal_sel != "Semua portal":
        df_filtered = df_filtered[df_filtered["portal"] == portal_sel]
    if kategori_sel != "Semua kategori":
        df_filtered = df_filtered[df_filtered["kategori"] == kategori_sel]

    st.caption(f"{len(df_filtered):,} artikel cocok dengan saringan di atas.")

    rule()

    # ── Topic browser ────────────────────────────────────────────────
    kicker(f"Model · {MODEL_DISPLAY_NAMES[model_col]}")
    st.markdown("#### Sebaran topik")

    topic_counts = (
        df_filtered[model_col].value_counts().sort_index().reset_index()
    )
    topic_counts.columns = ["topic_id", "jumlah"]
    topic_counts["label"] = topic_counts["topic_id"].apply(
        lambda t: f"T{t} · {label_for(model_col, t)}"
    )

    c1, c2 = st.columns([1.4, 1])

    with c1:
        sorted_counts = topic_counts.sort_values("jumlah", ascending=True)
        bar_color = MODEL_COLORS.get(MODEL_DISPLAY_NAMES[model_col], "#6B6258")
        fig = go.Figure(go.Bar(
            x=sorted_counts["jumlah"], y=sorted_counts["label"], orientation="h",
            marker_color=bar_color,
        ))
        fig.update_layout(
            height=540,
            font=dict(family="JetBrains Mono, monospace", size=10, color="#1F1B16"),
            plot_bgcolor="#FAF7F0", paper_bgcolor="#FAF7F0",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        fig.update_xaxes(title="Jumlah artikel", showgrid=True, gridcolor="#EFE9DB")
        fig.update_yaxes(showgrid=False)
        ui.plotly_chart(fig)

    with c2:
        topic_options = topic_counts.sort_values("jumlah", ascending=False)
        selected_label = st.selectbox(
            "Buka topik", options=topic_options["label"].tolist(),
        )
        selected_id = int(selected_label.split(" ")[0][1:])

        df_topic = df_filtered[df_filtered[model_col] == selected_id]
        st.metric("Artikel pada topik ini", f"{len(df_topic):,}")

        if len(df_topic) > 0:
            kat_dist = df_topic["kategori"].value_counts().reset_index()
            kat_dist.columns = ["kategori", "jumlah"]
            colors = [KATEGORI_COLORS.get(k, "#6B6258") for k in kat_dist["kategori"]]
            total = kat_dist["jumlah"].sum()
            # Sembunyikan label persen untuk slice yang sangat kecil agar tidak bertumpuk
            text_template = [
                f"{v/total:.1%}" if v / total >= 0.04 else ""
                for v in kat_dist["jumlah"]
            ]
            fig2 = go.Figure(go.Pie(
                labels=kat_dist["kategori"], values=kat_dist["jumlah"],
                hole=0.5, marker=dict(colors=colors),
                text=text_template, textinfo="text",
                textposition="inside",
                textfont=dict(family="JetBrains Mono, monospace", size=10),
            ))
            fig2.update_layout(
                height=340,
                font=dict(family="JetBrains Mono, monospace", size=10, color="#1F1B16"),
                paper_bgcolor="#FAF7F0",
                margin=dict(l=10, r=10, t=40, b=10),
                title=dict(text="Kategori pada topik ini", font=dict(family="Source Serif 4, serif", size=13)),
                showlegend=True,
                legend=dict(font=dict(size=9), orientation="v", x=1.05, y=0.5, yanchor="middle"),
            )
            ui.plotly_chart(fig2)

    rule()

    # ── Search & table ────────────────────────────────────────────────
    kicker("Pencarian")
    st.markdown("#### Cari artikel")

    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        query = st.text_input(
            "Judul mengandung", placeholder="contoh: rupiah, MotoGP, kurban...",
            label_visibility="visible",
        )
    with search_col2:
        only_selected_topic = st.checkbox(f"Hanya topik T{selected_id}", value=False)

    df_view = df_filtered
    if only_selected_topic:
        df_view = df_view[df_view[model_col] == selected_id]
    if query:
        df_view = df_view[df_view["judul"].str.contains(query, case=False, na=False)]

    display_cols = ["portal", "kategori", "judul", "topic_lda", "topic_nmf", "topic_bertopic"]
    display_cols = [c for c in display_cols if c in df_view.columns]

    df_show = df_view[display_cols].head(200).copy()
    df_show[f"label_{MODEL_DISPLAY_NAMES[model_col].lower()}"] = df_show[model_col].apply(
        lambda t: label_for(model_col, t)
    )

    st.caption(f"{len(df_show):,} dari {len(df_view):,} artikel cocok (maksimal 200 baris).")
    ui.df(df_show, hide_index=True)

    rule()

    # ── pyLDAvis ─────────────────────────────────────────────────────
    kicker("LDA — pyLDAvis")
    st.markdown("#### Peta topik interaktif")

    pyldavis_path = static_figure_path("pyldavis_output.html")
    if pyldavis_path:
        with open(pyldavis_path, "r", encoding="utf-8") as f:
            html = f.read()
        st.components.v1.html(html, height=800, scrolling=True)
    else:
        st.caption("`output/pyldavis_output.html` tidak ditemukan — peta dilewati.")
