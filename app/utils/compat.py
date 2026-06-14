"""
Shim kompatibilitas untuk parameter "width" / "use_container_width".

Beberapa versi Streamlit yang beredar saat ini tidak konsisten:
  - Versi lama: st.image/st.dataframe/st.plotly_chart pakai use_container_width=True
  - Versi baru: semuanya pakai width="stretch"
  - Versi transisi (beberapa instalasi conda terbaru): st.image sudah
    menolak use_container_width, TAPI st.dataframe masih menolak
    width="stretch" (mengharapkan int).

Daripada menebak versi, fungsi di bawah mencoba width="stretch" dulu,
lalu fallback ke use_container_width=True, lalu fallback polos tanpa
argumen lebar sama sekali -- supaya app tidak crash di kombinasi
versi manapun.
"""

import streamlit as st


def df(data, **kwargs):
    """st.dataframe yang aman lintas versi Streamlit."""
    try:
        return st.dataframe(data, width="stretch", **kwargs)
    except TypeError:
        try:
            return st.dataframe(data, use_container_width=True, **kwargs)
        except TypeError:
            return st.dataframe(data, **kwargs)


def image(path, **kwargs):
    """st.image yang aman lintas versi Streamlit."""
    try:
        return st.image(path, width="stretch", **kwargs)
    except TypeError:
        try:
            return st.image(path, use_container_width=True, **kwargs)
        except TypeError:
            return st.image(path, **kwargs)


def plotly_chart(fig, **kwargs):
    """st.plotly_chart yang aman lintas versi Streamlit."""
    try:
        return st.plotly_chart(fig, width="stretch", **kwargs)
    except TypeError:
        try:
            return st.plotly_chart(fig, use_container_width=True, **kwargs)
        except TypeError:
            return st.plotly_chart(fig, **kwargs)
