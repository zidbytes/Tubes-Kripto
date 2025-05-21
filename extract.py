import cv2
import numpy as np
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from skimage.metrics import structural_similarity as ssim

def decrypt_image_aes(cipher_array: np.ndarray, key: bytes, iv: bytes, shape) -> np.ndarray:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(cipher_array.tobytes()), AES.block_size)
    return np.frombuffer(decrypted, dtype=np.uint8).reshape(shape)

def extract_svd(watermarked: np.ndarray, original: np.ndarray, alpha=0.05, length=64) -> np.ndarray:
    _, S_wm, _ = np.linalg.svd(watermarked.astype(np.float64), full_matrices=False)
    _, S_orig, _ = np.linalg.svd(original.astype(np.float64), full_matrices=False)
    diff = (S_wm - S_orig) / alpha
    return np.round(diff[:length]).astype(np.uint8)

def calculate_metrics(original: np.ndarray, extracted: np.ndarray):
    assert original.shape == extracted.shape, "Image shapes must match"

    # PSNR
    mse = np.mean((original.astype(np.float32) - extracted.astype(np.float32)) ** 2)
    psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse != 0 else float('inf')

    # SSIM
    ssim_score = ssim(original, extracted, data_range=255)

    # BER
    orig_bits = np.unpackbits(original.astype(np.uint8))
    extr_bits = np.unpackbits(extracted.astype(np.uint8))
    ber = np.sum(orig_bits != extr_bits) / len(orig_bits)

    # Fidelity Difference (FD)
    fd = np.mean(np.abs(original.astype(np.int32) - extracted.astype(np.int32)))

    print("\nEvaluasi Watermark:")
    print(f"PSNR : {psnr:.2f} dB")
    print(f"SSIM : {ssim_score:.4f}")
    print(f"BER  : {ber:.4%}")
    print(f"FD   : {fd:.4f}")

def extract_and_decrypt(output_dir):
    video_path = os.path.join(output_dir, 'output.mp4')  # <-- GANTI sesuai file yang sedang diuji
    cipher_path = os.path.join(output_dir, 'cipher.bin')
    meta_path = os.path.join(output_dir, 'embed_meta.npz')
    recovered_path = os.path.join(output_dir, 'recovered_watermark.png')

    print(f"🔍 Mencoba membuka video: {video_path}")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"❌ Gagal membuka video: {video_path}")

    ret, frame = cap.read()
    if not ret:
        raise ValueError(f"❌ Gagal membaca frame pertama dari: {video_path}")
    print(f"✅ Frame pertama berhasil dibaca, shape: {frame.shape}")

    # --- Lanjutkan normal ---
    meta = np.load(meta_path, allow_pickle=True)
    key = meta['key'].tobytes()
    iv = meta['iv'].tobytes()
    shape = tuple(meta['shape'])
    original_frame = meta['original_frame']
    hash_expected = meta['hash_vector']

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    extracted_hash = extract_svd(gray, original_frame, alpha=0.05, length=len(hash_expected))
    cap.release()

<<<<<<< HEAD
    print("✅ Hash berhasil diekstraksi dari frame pertama.")
    match = np.array_equal(extracted_hash, hash_expected)
    print("🧬 Hash cocok:", match)
=======
    print("✅ Hash berhasil diekstraksi.")
    # print("🧬 Hash cocok:", np.array_equal(extracted_hash, hash_expected))
>>>>>>> ada300257b605d8d21064201f52147ffad1c9b07

    with open(cipher_path, 'rb') as f:
        cipher = np.frombuffer(f.read(), dtype=np.uint8)
    wm_reconstructed = decrypt_image_aes(cipher, key, iv, shape)
    cv2.imwrite(recovered_path, wm_reconstructed)

    # Evaluasi kualitas watermark
    wm_original = cv2.imread(os.path.join(output_dir, "..", "media", "input.jpg"), cv2.IMREAD_GRAYSCALE)
    wm_original = cv2.resize(wm_original, (wm_reconstructed.shape[1], wm_reconstructed.shape[0]))

    calculate_metrics(wm_original, wm_reconstructed)

    return recovered_path, match

