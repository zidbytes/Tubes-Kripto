# extract.py
import cv2
import numpy as np
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_image_aes(cipher_array: np.ndarray, key: bytes, iv: bytes, shape) -> np.ndarray:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(cipher_array.tobytes()), AES.block_size)
    return np.frombuffer(decrypted, dtype=np.uint8).reshape(shape)

def extract_svd(watermarked: np.ndarray, original: np.ndarray, alpha=0.05, length=64) -> np.ndarray:
    _, S_wm, _ = np.linalg.svd(watermarked.astype(np.float64), full_matrices=False)
    _, S_orig, _ = np.linalg.svd(original.astype(np.float64), full_matrices=False)
    diff = (S_wm - S_orig) / alpha
    return np.round(diff[:length]).astype(np.uint8)

def extract_and_decrypt(output_dir):
    video_path = os.path.join(output_dir, 'output.mp4')
    cipher_path = os.path.join(output_dir, 'cipher.bin')
    meta_path = os.path.join(output_dir, 'embed_meta.npz')
    recovered_path = os.path.join(output_dir, 'recovered_watermark.png')

    meta = np.load(meta_path, allow_pickle=True)
    key = meta['key'].tobytes()
    iv = meta['iv'].tobytes()
    shape = tuple(meta['shape'])
    original_frame = meta['original_frame']
    hash_expected = meta['hash_vector']

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        raise ValueError("❌ Gagal membaca video output.")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    extracted_hash = extract_svd(gray, original_frame, alpha=0.05, length=len(hash_expected))
    cap.release()

    print("Hash berhasil diekstraksi.")
    print("", np.array_equal(extracted_hash, hash_expected))

    with open(cipher_path, 'rb') as f:
        cipher = np.frombuffer(f.read(), dtype=np.uint8)
    wm = decrypt_image_aes(cipher, key, iv, shape)
    cv2.imwrite(recovered_path, wm)

    return recovered_path, np.array_equal(extracted_hash, hash_expected)
