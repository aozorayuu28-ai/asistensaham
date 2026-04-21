import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Tampilan Halaman
st.set_page_config(page_title="Analisis Saham Pribadi", page_icon="🔍", layout="centered")

# Fungsi Rumus RSI
def hitung_rsi(data, periode=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/periode, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/periode, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Bagian Header Website
st.title("🔍 Ayo Mulai Analisis")
st.write("Ketik kode saham, dan saya akan memberikan analisis serta penjelasan yang mudah dipahami!")

# Kotak Pencarian
search_query = st.text_input("🔍 Masukkan Kode Saham (contoh: BBCA, GOTO, TLKM):", "").upper()

st.write("dibuat oleh orang gabut contact me jika terdapat kendala @v.pratamaa on instagram!")
if search_query:
    # Memastikan format kode saham sesuai dengan Yahoo Finance (tambah .JK untuk saham Indonesia)
    if not search_query.endswith('.JK'):
        symbol = search_query + '.JK'
    else:
        symbol = search_query

    with st.spinner(f"Sedang menganalisis {search_query}..."):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo")
            info = ticker.info

            if data.empty:
                st.error(f"❌ Saham '{search_query}' tidak ditemukan atau data tidak tersedia. Pastikan kodenya benar.")
            else:
                # Mengambil data harga terbaru
                harga_terakhir = data['Close'].iloc[-1]
                harga_kemarin = data['Close'].iloc[-2]
                perubahan = harga_terakhir - harga_kemarin
                persen_perubahan = (perubahan / harga_kemarin) * 100

                # 1. MENAMPILKAN HARGA & GRAFIK
                st.subheader(f"Pergerakan Harga: {search_query.replace('.JK', '')}")
                
                # Menampilkan harga dengan warna otomatis (Hijau naik, Merah turun)
                st.metric(label="Harga Saat Ini", 
                          value=f"Rp {harga_terakhir:,.0f}", 
                          delta=f"{perubahan:,.0f} ({persen_perubahan:.2f}%)")

                # Menampilkan Grafik Garis bawaan Streamlit
                st.line_chart(data['Close'], use_container_width=True)

                st.divider()

                # 2. MENGHITUNG INDIKATOR
                data['RSI_14'] = hitung_rsi(data, 14)
                data['SMA_20'] = data['Close'].rolling(window=20).mean()
                rsi_terakhir = data['RSI_14'].iloc[-1]
                sma20 = data['SMA_20'].iloc[-1]
                
                per = info.get('trailingPE', 0)
                if per is None: per = 0 # Mencegah error jika data kosong
                
                pbv = info.get('priceToBook', 0)
                if pbv is None: pbv = 0
                
                div_yield = (info.get('dividendYield', 0) or 0) * 100

                # 3. MENAMPILKAN RAPOR SAHAM (Ramah Pemula)
                st.subheader("📚 Rapor & Penjelasan Pemula")
                
                # Membuat 2 kolom agar rapi
                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"**⚡ RSI (Momentum): {rsi_terakhir:.1f}**\n\n"
                            "*Apa artinya?* Ini seperti termometer belanja. Jika angka di bawah 30, artinya saham sedang 'Oversold' (banyak yang jual, berpotensi mantul naik). Jika di atas 70, artinya sudah 'Overbought' (terlalu mahal/rawan turun).\n\n"
                            f"**Status:** {'Diskon (Oversold)' if rsi_terakhir < 30 else 'Rawan Turun (Overbought)' if rsi_terakhir > 70 else 'Normal'}")
                    
                    st.success(f"**📈 Tren (MA-20): Rp {sma20:,.0f}**\n\n"
                               "*Apa artinya?* Ini adalah rata-rata harga sebulan terakhir. Jika harga saat ini di atas rata-rata ini, berarti tren saham sedang bagus (Uptrend).\n\n"
                               f"**Status:** {'Tren Naik (Bagus)' if harga_terakhir > sma20 else 'Tren Turun (Hati-hati)'}")

                with col2:
                    st.warning(f"**🏷️ PER (Valuasi): {per:.1f}x**\n\n"
                               "*Apa artinya?* Butuh berapa tahun agar perusahaan bisa balik modal jika Anda beli sahamnya sekarang. Semakin kecil angkanya (biasanya di bawah 15), semakin murah sahamnya.\n\n"
                               f"**Status:** {'Murah' if 0 < per < 15 else 'Mahal/Rugi'}")

                    st.error(f"**🏢 PBV (Harga Asli): {pbv:.1f}x**\n\n"
                             "*Apa artinya?* Ibarat membeli rumah, apakah Anda beli di atas atau di bawah harga aslinya? Angka 1 berarti pas. Di bawah 1 berarti Anda beli harga diskon.\n\n"
                             f"**Status:** {'Sangat Murah' if 0 < pbv < 1 else 'Wajar/Mahal'}")

                # 4. KESIMPULAN ASISTEN
                st.subheader("🤖 Kesimpulan Asisten")
                if rsi_terakhir < 35 and harga_terakhir > harga_kemarin:
                    st.success("🟢 **Rekomendasi:** Berpotensi untuk dibeli (Trading Jangka Pendek). Harganya sedang di bawah dan mulai ada pantulan naik.")
                elif (0 < per < 15) and (0 < pbv < 1.5):
                    st.success("🏦 **Rekomendasi:** Cocok untuk Investasi Jangka Panjang. Secara hitungan bisnis, perusahaan ini sedang dihargai cukup murah oleh pasar.")
                elif harga_terakhir < sma20:
                    st.warning("🟡 **Rekomendasi:** Wait & See (Tunggu dulu). Tren harganya masih cenderung turun. Lebih baik pantau dulu sampai harganya stabil.")
                else:
                    st.info("⚪ **Rekomendasi:** Netral. Saham ini sedang bergerak wajar, tidak terlalu murah dan belum ada momentum kenaikan yang kuat.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat mengambil data. Pastikan koneksi internet stabil atau coba lagi nanti. (Pesan: {e})")
