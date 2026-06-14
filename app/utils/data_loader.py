"""
Helper untuk load data hasil S1, S2, S3.

Semua fungsi memakai st.cache_data agar file hanya dibaca sekali
per sesi (penting untuk topic_labels.csv yang berukuran ~20k baris).

Jika file tidak ditemukan, fungsi mengembalikan None / DataFrame kosong
dan halaman terkait akan menampilkan pesan "data belum tersedia"
alih-alih error -- supaya app tidak crash saat salah satu skenario
belum selesai diekspor.

PATH RESOLUTION
---------------
File ini ada di <repo>/<app_folder>/utils/data_loader.py, sedangkan
folder output/ ada di <repo>/output/. Karena <app_folder> bisa berbeda
nama (app/, atau app.py langsung di root repo), kita cari folder
"output" dengan naik dari lokasi file ini, maksimal 3 level, dan
ambil yang pertama ditemukan.
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st


def _find_repo_root(start: str, marker: str = "output", max_up: int = 3) -> str:
    """Naik dari `start` mencari folder yang punya subfolder `marker`."""
    current = start
    for _ in range(max_up + 1):
        if os.path.isdir(os.path.join(current, marker)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # fallback: dua level di atas file ini (struktur app/utils/)
    return os.path.dirname(os.path.dirname(start))


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = _find_repo_root(_THIS_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
S3_DIR = os.path.join(OUTPUT_DIR, "s3")


def _read_csv_safe(path: str, **kwargs) -> pd.DataFrame | None:
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path, **kwargs)
    except Exception as e:  # noqa: BLE001
        st.warning(f"Gagal membaca {os.path.basename(path)}: {e}")
        return None


@st.cache_data(show_spinner="Memuat data label topik...")
def load_topic_labels() -> pd.DataFrame | None:
    """Output utama S1 — topic_labels.csv (20.334 baris).

    Kolom penting:
        portal, kategori, judul,
        topic_lda, topic_nmf, topic_bertopic, bertopic_outlier,
        lda_prob_t0..lda_prob_t24
    """
    df = _read_csv_safe(os.path.join(OUTPUT_DIR, "topic_labels.csv"))
    if df is None:
        return None

    # Pastikan tipe data konsisten untuk filter
    for col in ["topic_lda", "topic_nmf", "topic_bertopic"]:
        if col in df.columns:
            df[col] = df[col].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_s1_comparison() -> pd.DataFrame | None:
    """Tabel perbandingan coherence LDA/NMF/BERTopic per k — Skenario S1."""
    return _read_csv_safe(os.path.join(OUTPUT_DIR, "topic_model_comparison_s1.csv"))


@st.cache_data(show_spinner=False)
def load_s2_results() -> pd.DataFrame | None:
    """Hasil Optuna hyperparameter search UMAP+HDBSCAN -- Skenario S2.

    File: <repo_root>/hasil_optuna_hyperparameter.csv
    """
    return _read_csv_safe(os.path.join(BASE_DIR, "hasil_optuna_hyperparameter.csv"))


@st.cache_data(show_spinner=False)
def load_s3_comparison() -> pd.DataFrame | None:
    """Tabel perbandingan 5 model embedding — Skenario S3."""
    return _read_csv_safe(os.path.join(S3_DIR, "s3_embedding_comparison.csv"))


@st.cache_data(show_spinner=False)
def load_s3_topic_words() -> dict | None:
    """Top words per topik untuk masing-masing model embedding (S3)."""
    path = os.path.join(S3_DIR, "s3_topic_words_per_model.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_s3_topic_assignments() -> pd.DataFrame | None:
    """Topic assignment per dokumen untuk masing-masing model embedding (S3)."""
    return _read_csv_safe(os.path.join(S3_DIR, "s3_topic_assignments.csv"))


def static_figure_path(filename: str, subdir: str | None = None) -> str | None:
    """Mengembalikan path absolut ke gambar statis di output/ (atau output/s3/)
    jika file ada, sebaliknya None."""
    folder = S3_DIR if subdir == "s3" else OUTPUT_DIR
    path = os.path.join(folder, filename)
    return path if os.path.exists(path) else None


def debug_paths() -> dict:
    """Info path untuk troubleshooting -- ditampilkan di sidebar bila perlu."""
    return {
        "this_file_dir": _THIS_DIR,
        "base_dir": BASE_DIR,
        "output_dir": OUTPUT_DIR,
        "output_dir_exists": os.path.isdir(OUTPUT_DIR),
        "s3_dir_exists": os.path.isdir(S3_DIR),
        "topic_labels_exists": os.path.exists(os.path.join(OUTPUT_DIR, "topic_labels.csv")),
        "s2_csv_exists": os.path.exists(os.path.join(BASE_DIR, "hasil_optuna_hyperparameter.csv")),
        "s3_csv_exists": os.path.exists(os.path.join(S3_DIR, "s3_embedding_comparison.csv")),
    }
