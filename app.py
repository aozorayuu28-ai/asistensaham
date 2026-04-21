import streamlit as st
import yfinance as yf
import pandas as pd
from PIL import Image # Tambahkan library ini untuk membaca gambar

# Konfigurasi Tampilan Halaman
st.set_page_config(page_title="ashapri - Asisten Saham", page_icon="📈", layout="centered")

# --- MENAMPILKAN LOGO DI SIDEBAR ---
try:
    # Membuka file gambar logo
    image = Image.open('logo.png')
    
    # Menampilkan gambar di sidebar dengan lebar yang disesuaikan
    st.sidebar.image(image, use_container_width=True)
    
    # Menambahkan garis pembatas tipis di bawah logo agar rapi
    st.sidebar.markdown("---")
except FileNotFoundError:
    # Jika file gambar tidak ditemukan, tampilkan teks saja di sidebar
    st.sidebar.title("💎 ashapri")
    st.sidebar.write("Asisten Saham Pribadi")

# --- LANJUTAN KODE ANDA YANG SEBELUMNYA ---
# (Fungsi Rumus RSI, Judul Utama, Kotak Pencarian, dll.)
# ...
