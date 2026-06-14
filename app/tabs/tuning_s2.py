"""
Tuning BERTopic — Skenario S2.

Optuna (TPE Sampler) mencari kombinasi parameter UMAP + HDBSCAN yang
memaksimalkan Coherence Cᵥ. File sumber: <repo_root>/hasil_optuna_hyperparameter.csv
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.theme import kicker, rule
from utils import compat as ui


def render(df_s2: pd.DataFrame | None) -> None:
    kicker("Skenario 2")
    st.markdown("#### Mencari konfigurasi UMAP + HDBSCAN")
    st.caption(
        "Optuna menjalankan beberapa percobaan (trial), tiap trial mencoba "
        "kombinasi parameter berbeda dan dinilai dari Coherence Cᵥ yang dihasilkan."
    )

    if df_s2 is None:
        st.warning(
            "`hasil_optuna_hyperparameter.csv` belum ditemukan di root repo. "
            "Cek panel **Diagnostik path data** di sidebar untuk lokasi yang dicari, "
            "atau pastikan file sudah ter-commit."
        )
        return

    # Cari kolom coherence secara fleksibel (nama bisa coherence_cv / coherence / C_v)
    coherence_col = next(
        (c for c in df_s2.columns if "coher" in c.lower()), None
    )
    n_topics_col = next(
        (c for c in df_s2.columns if "n_topic" in c.lower() or c.lower() == "topik"), None
    )
    outlier_col = next(
        (c for c in df_s2.columns if "outlier" in c.lower() or "noise" in c.lower()), None
    )
    trial_col = next(
        (c for c in df_s2.columns if "trial" in c.lower()), df_s2.index.name or None
    )

    if coherence_col is None:
        st.error(
            "Tidak menemukan kolom coherence pada file CSV. Kolom yang tersedia: "
            + ", ".join(df_s2.columns)
        )
        ui.df(df_s2, hide_index=True)
        return

    df_sorted = df_s2.sort_values(coherence_col, ascending=False).reset_index(drop=True)
    best = df_sorted.iloc[0]

    # ── Headline numbers ──────────────────────────────────────────────
    cols = st.columns(4)
    cols[0].metric("Percobaan", len(df_sorted))
    cols[1].metric("Cᵥ terbaik", f"{best[coherence_col]:.4f}")
    if n_topics_col:
        cols[2].metric("Jumlah topik (terbaik)", int(best[n_topics_col]))
    if outlier_col:
        val = best[outlier_col]
        pct = val * 100 if val <= 1 else val
        cols[3].metric("Outlier (terbaik)", f"{pct:.1f}%")

    rule()

    # ── Scatter: coherence vs outlier, size by n_topics ───────────────
    kicker("Trade-off")
    st.markdown("#### Coherence vs proporsi outlier")

    c1, c2 = st.columns([3, 2])
    with c1:
        if outlier_col and n_topics_col:
            outlier_vals = df_sorted[outlier_col]
            if outlier_vals.max() <= 1:
                outlier_vals = outlier_vals * 100

            fig = go.Figure(go.Scatter(
                x=outlier_vals, y=df_sorted[coherence_col],
                mode="markers",
                marker=dict(
                    size=df_sorted[n_topics_col],
                    sizemode="area",
                    sizeref=2. * df_sorted[n_topics_col].max() / (40. ** 2),
                    sizemin=4,
                    color=df_sorted[coherence_col],
                    colorscale=[[0, "#D9D2C4"], [1, "#8B3A3A"]],
                    showscale=False,
                    line=dict(width=1, color="#1F1B16"),
                ),
                text=[f"trial {t}, {n} topik" for t, n in zip(
                    df_sorted[trial_col] if trial_col else df_sorted.index,
                    df_sorted[n_topics_col],
                )],
                hovertemplate="%{text}<br>outlier %{x:.1f}%<br>Cᵥ %{y:.4f}<extra></extra>",
            ))
            fig.update_layout(
                height=400,
                font=dict(family="JetBrains Mono, monospace", size=11, color="#1F1B16"),
                plot_bgcolor="#FAF7F0", paper_bgcolor="#FAF7F0",
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
            )
            fig.update_xaxes(title="Outlier (%)", showgrid=True, gridcolor="#EFE9DB")
            fig.update_yaxes(title="Coherence Cᵥ", showgrid=True, gridcolor="#EFE9DB")
            ui.plotly_chart(fig)
            st.caption("Ukuran titik mencerminkan jumlah topik yang dihasilkan trial tersebut.")
        else:
            st.caption("Kolom outlier/jumlah topik tidak ditemukan — scatter dilewati.")

    with c2:
        st.markdown("**Tabel percobaan (diurutkan Cᵥ)**")
        cols_priority = ["rank", trial_col, coherence_col, n_topics_col, outlier_col]
        cols_show = [c for c in cols_priority if c and c in df_sorted.columns]
        cols_show += [c for c in df_sorted.columns if c not in cols_show]
        ui.df(
            df_sorted[cols_show], hide_index=True, height=420,
        )

    rule()

    # ── Best config detail ─────────────────────────────────────────────
    kicker("Konfigurasi terpilih")
    st.markdown("#### Parameter percobaan terbaik")

    param_cols = [
        c for c in df_sorted.columns
        if c not in [coherence_col, n_topics_col, outlier_col, trial_col, "rank"]
    ]
    if param_cols:
        n_per_row = 4
        for i in range(0, len(param_cols), n_per_row):
            row_cols = st.columns(n_per_row)
            for j, pname in enumerate(param_cols[i:i + n_per_row]):
                val = best[pname]
                if isinstance(val, float):
                    display_val = f"{val:.0f}" if val == int(val) and abs(val) >= 1 else f"{val:.4f}"
                else:
                    display_val = str(val)
                row_cols[j].metric(pname, display_val)
