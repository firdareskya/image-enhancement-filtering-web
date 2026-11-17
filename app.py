import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="Image Enhancement & Filtering",
    page_icon="🖼️",
    layout="wide"
)

st.title("Image Enhancement & Image Filtering")
st.caption("Analisis Salt & Pepper Noise, Histogram Equalization, dan Median Filter")

def read_image(uploaded_file):
    data = np.frombuffer(uploaded_file.read(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    return img

def read_default_image(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return img

def tambah_salt_pepper(img, persen, seed=42):
    p = persen / 100.0
    rng = np.random.RandomState(seed)
    acak = rng.rand(*img.shape)
    noisy = img.copy()
    noisy[acak < p / 2] = 0
    noisy[acak > 1 - p / 2] = 255
    return noisy

def enhancement(img, level=256):
    hist = np.bincount(img.ravel(), minlength=level)
    cdf = np.cumsum(hist)
    w = np.floor(cdf * (level - 1) / img.size + 0.5)
    lut = np.clip(w, 0, level - 1).astype(np.uint8)
    return lut[img]

def filtering(img, k):
    return cv2.medianBlur(img, k)

def metrics(img):
    return f"Rata-rata: {img.mean():.1f} | Median: {np.median(img):.0f} | Std: {img.std():.1f}"

def show_image_and_hist(title, img):
    col_img, col_hist = st.columns([1, 1])
    with col_img:
        st.image(img, caption=title, use_container_width=True, clamp=True)
        st.caption(metrics(img))
    with col_hist:
        fig, ax = plt.subplots(figsize=(5, 2.6))
        hist = np.bincount(img.ravel(), minlength=256)
        ax.vlines(np.arange(256), 0, hist, linewidth=1)
        ax.set_xlim(-2, 257)
        ax.set_title("Histogram")
        ax.set_xlabel("Intensitas piksel")
        ax.set_ylabel("Jumlah piksel")
        ax.grid(alpha=0.2)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with st.sidebar:
    st.header("Pengaturan")
    uploaded = st.file_uploader(
        "Pilih citra sendiri (opsional)",
        type=["jpg", "jpeg", "png", "bmp", "tif", "tiff"]
    )
    noise = st.select_slider(
        "Persentase Noise",
        options=[1, 2, 5, 10, 15, 20, 30, 40, 50],
        value=10,
        format_func=lambda x: f"{x}%"
    )
    kernel_label = st.selectbox("Kernel Median Filter", ["3 x 3", "5 x 5", "7 x 7"])
    kernel = int(kernel_label[0])
    scenario = st.radio(
        "Pilih tampilan",
        [
            "Citra Asli → Noise Salt & Pepper",
            "Skenario A: Enhancement saja",
            "Skenario B: Filtering saja",
            "Skenario C: Enhancement → Filtering",
            "Skenario D: Filtering → Enhancement",
            "Bandingkan Skenario C vs D"
        ]
    )
    st.divider()
    st.caption("Zoom gambar dapat dilakukan menggunakan fitur zoom browser atau membuka gambar di tab baru.")

if uploaded is not None:
    uploaded.seek(0)
    original = read_image(uploaded)
else:
    default_path = Path(__file__).parent / "Tomat.jpg"
    original = read_default_image(default_path)

if original is None:
    st.error("Gambar tidak dapat dibaca. Unggah gambar JPG atau PNG yang valid.")
    st.stop()

noisy = tambah_salt_pepper(original, noise)
he = enhancement(noisy)
median = filtering(noisy, kernel)
c_result = filtering(he, kernel)
d_median = filtering(noisy, kernel)
d_result = enhancement(d_median)

st.info(
    f"Noise: {noise}%  |  Kernel Median: {kernel} x {kernel}  |  "
    f"Ukuran citra: {original.shape[1]} × {original.shape[0]} piksel"
)

if scenario == "Citra Asli → Noise Salt & Pepper":
    st.subheader("Citra Asli dan Citra dengan Noise")
    cols = st.columns(2)
    with cols[0]:
        show_image_and_hist("Citra Asli", original)
    with cols[1]:
        show_image_and_hist(f"Noise Salt & Pepper ({noise}%)", noisy)

elif scenario == "Skenario A: Enhancement saja":
    st.subheader("Skenario A — Histogram Equalization")
    st.write("Histogram Equalization meningkatkan sebaran intensitas dan kontras. Noise tetap terbawa.")
    cols = st.columns(3)
    for col, title, img in zip(
        cols,
        ["Citra Asli", "Citra dengan Noise", "Hasil Histogram Equalization"],
        [original, noisy, he]
    ):
        with col:
            show_image_and_hist(title, img)

elif scenario == "Skenario B: Filtering saja":
    st.subheader("Skenario B — Median Filter")
    st.write("Median Filter mengganti nilai piksel dengan median dari lingkungan piksel di sekitarnya untuk mengurangi bintik salt & pepper.")
    cols = st.columns(3)
    for col, title, img in zip(
        cols,
        ["Citra Asli", "Citra dengan Noise", f"Hasil Median Filter {kernel}×{kernel}"],
        [original, noisy, median]
    ):
        with col:
            show_image_and_hist(title, img)

elif scenario == "Skenario C: Enhancement → Filtering":
    st.subheader("Skenario C — Histogram Equalization lalu Median Filter")
    st.write("Tahap 1: Histogram Equalization. Tahap 2: Median Filter.")
    cols = st.columns(4)
    for col, title, img in zip(
        cols,
        ["Citra Asli", "Citra dengan Noise", "Langkah 1: Histogram Equalization", f"Langkah 2: Median Filter {kernel}×{kernel}"],
        [original, noisy, he, c_result]
    ):
        with col:
            show_image_and_hist(title, img)

elif scenario == "Skenario D: Filtering → Enhancement":
    st.subheader("Skenario D — Median Filter lalu Histogram Equalization")
    st.write("Tahap 1: Median Filter untuk mengurangi noise. Tahap 2: Histogram Equalization untuk memperbaiki kontras.")
    cols = st.columns(4)
    for col, title, img in zip(
        cols,
        ["Citra Asli", "Citra dengan Noise", f"Langkah 1: Median Filter {kernel}×{kernel}", "Langkah 2: Histogram Equalization"],
        [original, noisy, d_median, d_result]
    ):
        with col:
            show_image_and_hist(title, img)

else:
    st.subheader("Perbandingan Skenario C dan D")
    st.write("C: Histogram Equalization → Median Filter. D: Median Filter → Histogram Equalization.")
    cols = st.columns(4)
    for col, title, img in zip(
        cols,
        ["Citra Asli", "Citra dengan Noise", f"Skenario C: HE → Median {kernel}×{kernel}", f"Skenario D: Median {kernel}×{kernel} → HE"],
        [original, noisy, c_result, d_result]
    ):
        with col:
            show_image_and_hist(title, img)

st.divider()
st.subheader("Simpan Hasil")
download_choice = st.selectbox(
    "Pilih citra yang ingin diunduh",
    ["Citra Asli", "Citra dengan Noise", "Hasil Enhancement", "Hasil Filtering",
     "Hasil Skenario C", "Hasil Skenario D"]
)
image_options = {
    "Citra Asli": original,
    "Citra dengan Noise": noisy,
    "Hasil Enhancement": he,
    "Hasil Filtering": median,
    "Hasil Skenario C": c_result,
    "Hasil Skenario D": d_result
}
ok, encoded = cv2.imencode(".png", image_options[download_choice])
if ok:
    st.download_button(
        "⬇️ Download hasil (PNG)",
        data=encoded.tobytes(),
        file_name=download_choice.lower().replace(" ", "_") + ".png",
        mime="image/png"
    )

with st.expander("Penjelasan metode"):
    st.markdown("""
    - **Salt & Pepper Noise:** sebagian piksel diganti secara acak menjadi hitam (0) atau putih (255).
    - **Histogram Equalization:** memetakan ulang intensitas berdasarkan histogram kumulatif untuk meningkatkan kontras.
    - **Median Filter:** menggunakan nilai median dari tetangga piksel untuk mengurangi noise impulsif.
    - **Skenario C:** Enhancement dilakukan sebelum Filtering.
    - **Skenario D:** Filtering dilakukan sebelum Enhancement.
    """)
