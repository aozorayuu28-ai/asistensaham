import streamlit as st
import yfinance as yf
import pandas as pd
from PIL import Image

# 1. Konfigurasi Halaman (Elite Layout)
st.set_page_config(page_title="ashapri - Asisten Saham", page_icon="📈", layout="centered")

# 2. Fungsi Ambil Data dengan Caching (Anti-Error & Cepat)
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1y") # Ambil 1 tahun untuk analisis lebih akurat
    info = ticker.info
    return hist, info

# 3. Fungsi Indikator Teknikal
def hitung_rsi(data, periode=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/periode, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/periode, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 4. Tampilan Sidebar (Logo & Navigasi)
try:
    logo = Image.open('logo.png')
    st.sidebar.image(logo, use_container_width=True)
except:
    st.sidebar.title("💎 ashapri")

st.sidebar.write("---")
st.sidebar.markdown("### 🛠️ Fitur Asisten")
st.sidebar.write("- Analisis Teknikal (Short Term)")
st.sidebar.write("- Analisis Fundamental (Long Term)")
st.sidebar.write("- Manajemen Risiko (Stop Loss)")

# 5. Tampilan Utama
st.title("🔍 Pencari Saham Pintar")
st.write("Masukkan kode saham untuk mendapatkan analisis mendalam dan rekomendasi.")

search_query = st.text_input("Ketik kode saham (contoh: BBCA, ASII, ANTM):", "").upper()

if search_query:
    symbol = search_query if search_query.endswith('.JK') else search_query + '.JK'
    
    with st.spinner(f"Asisten sedang menganalisis {search_query}..."):
        try:
            hist, info = get_stock_data(symbol)

            if hist.empty:
                st.error("Saham tidak ditemukan. Pastikan kode benar (contoh: BBRI).")
            else:
                # --- BAGIAN 1: HARGA & GRAFIK ---
                harga_terakhir = hist['Close'].iloc[-1]
                harga_kemarin = hist['Close'].iloc[-2]
                perubahan = harga_terakhir - harga_kemarin
                persen = (perubahan / harga_kemarin) * 100

                st.metric(f"Harga {search_query}", f"Rp {harga_terakhir:,.0f}", f"{perubahan:,.0f} ({persen:.2f}%)")
                st.line_chart(hist['Close'])

                # --- BAGIAN 2: PERHITUNGAN ANALISIS ---
                hist['RSI_14'] = hitung_rsi(hist, 14)
                rsi = hist['RSI_14'].iloc[-1]
                sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                
                per = info.get('trailingPE', 0) or 0
                pbv = info.get('priceToBook', 0) or 0
                div_yield = (info.get('dividendYield', 0) or 0) * 100

                # --- BAGIAN 3: RAPOR EDUKASI (Ramah Pemula) ---
                st.subheader("📚 Rapor & Penjelasan")
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Momentum (RSI): {rsi:.1f}**\n\n*Indikator kejenuhan pasar. Di bawah 30 = Murah/Oversold.*")
                    st.success(f"**Tren (MA-20): Rp {sma20:,.0f}**\n\n*Harga rata-rata 20 hari terakhir.*")
                with c2:
                    st.warning(f"**Valuasi (PER): {per:.1f}x**\n\n*Balik modal dalam {per:.1f} tahun.*")
                    st.error(f"**Harga Asli (PBV): {pbv:.1f}x**\n\n*Harga dibanding nilai aset perusahaan.*")

                st.divider()

                # --- BAGIAN 4: REKOMENDASI JANGKA PENDEK & PANJANG ---
                st.subheader("🤖 Analisis Asisten Super Pintar")
                
                tab1, tab2 = st.tabs(["🚀 Jangka Pendek (Swing)", "🏦 Jangka Panjang (Invest)"])
                
                with tab1:
                    st.write("#### Strategi Trading (1-2 Minggu)")
                    if rsi < 40 and harga_terakhir > harga_kemarin:
                        st.success("✅ **SINYAL BELI:** Ada pantulan dari area murah. Cocok untuk beli sekarang.")
                        # Manajemen Risiko
                        target = harga_terakhir * 1.05
                        stop_loss = harga_terakhir * 0.96
                        st.write(f"🎯 **Target Jual (Profit):** Rp {target:,.0f} (+5%)")
                        st.write(f"🛡️ **Batas Rugi (Stop Loss):** Rp {stop_loss:,.0f} (-4%)")
                    elif rsi > 70:
                        st.error("❌ **JANGAN BELI:** Harga sudah terlalu tinggi (Overbought). Tunggu koreksi.")
                    else:
                        st.info("🟡 **WAIT & SEE:** Momentum belum kuat. Pantau terus pergerakannya.")

                with tab2:
                    st.write("#### Strategi Investasi (> 6 Bulan)")
                    if (0 < per < 15) and (0 < pbv < 2):
                        st.success(f"✅ **LAYAK INVESTASI:** Secara fundamental saham ini tergolong murah (Undervalued).")
                        if div_yield > 0: st.write(f"💰 **Bonus:** Dividen rutin sebesar {div_yield:.1f}% per tahun.")
                    else:
                        st.warning("⚠️ **VALUASI MAHAL:** Harga pasar jauh lebih tinggi dari nilai perusahaan. Berisiko untuk jangka panjang.")

        except Exception as e:
            if "Too Many Requests" in str(e):
                st.error("Yahoo Finance sedang membatasi akses. Tunggu 15 menit dan coba lagi.")
            else:
                st.error(f"Terjadi kesalahan teknis: {e}")
