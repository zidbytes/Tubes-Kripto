import cv2
import numpy as np
import pywt
from scipy.fftpack import dct, idct

def normalize_image(image):
    """Normalisasi citra ke rentang [0, 255]."""
    if np.max(image) != np.min(image):
        normalized = (image - np.min(image)) / (np.max(image) - np.min(image)) * 255
    else:
        normalized = np.zeros_like(image)
    return np.uint8(normalized)

def embed_image_in_video(video_path, image_path, output_path, embedding_strength=0.005):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Baca citra dan resize
    image = cv2.imread(image_path, 0)  # grayscale
    image = cv2.resize(image, (width, height)).astype(np.float32)

    print(f"[DEBUG] Citra asli - Min: {np.min(image)}, Max: {np.max(image)}")

    # DWT pada citra
    coeffs = pywt.dwt2(image, 'haar')
    LL, (LH, HL, HH) = coeffs

    print(f"[DEBUG] LL setelah DWT - Min: {np.min(LL)}, Max: {np.max(LL)}")

    # DCT pada LL citra
    LL_dct = dct(dct(LL.T).T)
    print(f"[DEBUG] LL setelah DCT - Min: {np.min(LL_dct)}, Max: {np.max(LL_dct)}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

        print(f"[DEBUG] Frame asli - Min: {np.min(gray)}, Max: {np.max(gray)}")

        # DWT pada frame
        coeffs_frame = pywt.dwt2(gray, 'haar')
        LLf, (LHf, HLf, HHf) = coeffs_frame

        print(f"[DEBUG] LL frame - Min: {np.min(LLf)}, Max: {np.max(LLf)}")

        # DCT pada LL frame
        LLf_dct = dct(dct(LLf.T).T)
        print(f"[DEBUG] LL frame setelah DCT - Min: {np.min(LLf_dct)}, Max: {np.max(LLf_dct)}")

        # Kurangi intensitas citra rahasia sebelum menyisipkan
        LL_dct_scaled = LL_dct * 0.05

        # Ganti bagian LL frame dengan LL citra
        LLf_dct[:LL_dct_scaled.shape[0], :LL_dct_scaled.shape[1]] = LLf_dct[:LL_dct_scaled.shape[0], :LL_dct_scaled.shape[1]] + embedding_strength * LL_dct_scaled

        # Inverse DCT
        LLf_idct = idct(idct(LLf_dct.T).T)

        # Rekonstruksi frame menggunakan IDWT
        merged = pywt.idwt2((LLf_idct, (LHf, HLf, HHf)), 'haar')

        # Normalisasi ke rentang [0, 255]
        merged = normalize_image(merged)

        # Konversi ke warna agar bisa dibaca OpenCV
        bgr = cv2.cvtColor(merged, cv2.COLOR_GRAY2BGR)

        # Tulis frame
        out.write(bgr)

        # Debug sebelum menyisipkan data
        print(f"[DEBUG] LL_dct sebelum penyisipan - Min: {np.min(LL_dct)}, Max: {np.max(LL_dct)}")
        # Debug setelah menyisipkan data
        print(f"[DEBUG] LLf_dct setelah penyisipan - Min: {np.min(LLf_dct)}, Max: {np.max(LLf_dct)}")

    cap.release()
    out.release()

def extract_image_from_video(video_path, output_image_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        raise Exception("Gagal membaca frame dari video")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
    coeffs = pywt.dwt2(gray, 'haar')
    LL, _ = coeffs

    LL_dct = dct(dct(LL.T).T)
    extracted = idct(idct(LL_dct.T).T)

    # Normalisasi dinamis
    if np.max(extracted) != np.min(extracted):
        extracted = (extracted - np.min(extracted)) / (np.max(extracted) - np.min(extracted)) * 255
    else:
        extracted = np.zeros_like(extracted)

    extracted = np.uint8(extracted)

    cv2.imwrite(output_image_path, extracted)
    cap.release()

    # Debug setelah ekstraksi
    print(f"[DEBUG] LL_dct setelah ekstraksi - Min: {np.min(LL_dct)}, Max: {np.max(LL_dct)}")
    print(f"[DEBUG] Extracted image - Min: {np.min(extracted)}, Max: {np.max(extracted)}")