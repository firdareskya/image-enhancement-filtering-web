# Image Enhancement & Image Filtering

Aplikasi web untuk menganalisis kombinasi Image Enhancement dan Image Filtering pada citra dengan Salt & Pepper Noise.

## Metode
- Noise: Salt & Pepper Noise
- Enhancement: Histogram Equalization
- Filtering: Median Filter
- Skenario C: Enhancement → Filtering
- Skenario D: Filtering → Enhancement

## Menjalankan secara lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, dan `Tomat.jpg` ke repository GitHub.
2. Buka https://share.streamlit.io/ dan login menggunakan GitHub.
3. Klik **Create app**.
4. Pilih repository, branch (biasanya `main`), dan file utama `app.py`.
5. Klik **Deploy**.
6. Setelah selesai, bagikan URL aplikasi kepada dosen atau orang lain.

Catatan: aplikasi ini adalah versi web dari program desktop Tkinter. Fitur utama pengolahan citra, pengaturan noise, pilihan kernel, histogram, perbandingan skenario, dan unduh hasil tersedia di browser.
