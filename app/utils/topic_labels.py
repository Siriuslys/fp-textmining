"""
Label semantik untuk topik hasil S1 (k=25 untuk LDA & NMF, 19 topik untuk BERTopic).

Label ini diturunkan secara manual dari top words tiap topik
(lihat 03_topic_modeling_s1.ipynb, Tabel 4.1-4.3 di laporan).

Jika kelompok ingin merevisi label, ubah dictionary di bawah —
seluruh tab akan otomatis menggunakan label terbaru karena
fungsi `label_for()` dipanggil setiap render.
"""

LDA_LABELS = {
    0: "Ekonomi & Industri",
    1: "MotoGP & Balap Motor",
    2: "Bulu Tangkis",
    3: "Nilai Tukar & Perbankan",
    4: "Hukum & Korupsi",
    5: "Kriminalitas & Kepolisian",
    6: "Otomotif & Kendaraan Listrik",
    7: "Kesehatan & Gaya Hidup",
    8: "Politik & Pemerintahan",
    9: "Infrastruktur & Transportasi",
    10: "Olahraga & Atletik",
    11: "Hiburan & Zodiak",
    12: "Selebriti & Media Sosial",
    13: "Travel & Kuliner",
    14: "Balap Motor Lokal",
    15: "Kesehatan & Konsumsi",
    16: "Pasar Saham & Investasi",
    17: "Pendidikan",
    18: "Pertanian & Pangan",
    19: "Energi & Sumber Daya Alam",
    20: "Teknologi & Gadget",
    21: "Cuaca & Bencana",
    22: "Keagamaan",
    23: "Geopolitik Internasional",
    24: "Properti & Perumahan",
}

NMF_LABELS = {
    0: "Ekonomi & Industri",
    1: "MotoGP & Balap Motor",
    2: "Bulu Tangkis",
    3: "Nilai Tukar & Perbankan",
    4: "Politik & Ekspor SDA",
    5: "Zodiak & Ramalan",
    6: "Kuliner & Restoran",
    7: "Berita Internasional & WNI",
    8: "Otomotif & Kendaraan Listrik",
    9: "Travel & Event",
    10: "Perbankan & Diskon",
    11: "Hiburan & Selebriti",
    12: "Balap Motor Lokal",
    13: "Kriminalitas & Kereta",
    14: "Kesehatan & Tubuh",
    15: "Olahraga & Atletik",
    16: "Pasar Saham",
    17: "Pendidikan",
    18: "Pertanian & Pangan",
    19: "Energi & SDA",
    20: "Teknologi & Gadget",
    21: "Cuaca & Bencana",
    22: "Keagamaan",
    23: "Geopolitik Internasional",
    24: "Properti & Perumahan",
}

BERTOPIC_LABELS = {
    -1: "Outlier / Multi-tema (noise)",
    0: "Pemerintahan & Digital",
    1: "Olahraga Umum",
    2: "Otomotif",
    3: "Teknologi & Gadget",
    4: "Transportasi",
    5: "Idul Adha & Kurban",
    6: "Pasar Saham",
    7: "Geopolitik",
    8: "Topik granular 8",
    9: "Topik granular 9",
    10: "Topik granular 10",
    11: "Topik granular 11",
    12: "Topik granular 12",
    13: "Topik granular 13",
    14: "Topik granular 14",
    15: "Topik granular 15",
    16: "Topik granular 16",
    17: "Topik granular 17",
    18: "Topik granular 18",
}

LABEL_MAPS = {
    "topic_lda": LDA_LABELS,
    "topic_nmf": NMF_LABELS,
    "topic_bertopic": BERTOPIC_LABELS,
}

MODEL_DISPLAY_NAMES = {
    "topic_lda": "LDA",
    "topic_nmf": "NMF",
    "topic_bertopic": "BERTopic",
}


def label_for(model_col: str, topic_id: int) -> str:
    """Kembalikan label semantik untuk topic_id pada model_col.
    Fallback ke 'Topik {id}' jika belum ada label terdaftar."""
    mapping = LABEL_MAPS.get(model_col, {})
    return mapping.get(int(topic_id), f"Topik {topic_id}")
