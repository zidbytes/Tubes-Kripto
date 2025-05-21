# embed.py
import cv2
import numpy as np
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import numpy as np

def encrypt_image_aes(image: np.ndarray, key: bytes):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    flat = image.flatten()
    ciphertext = cipher.encrypt(pad(flat.tobytes(), AES.block_size))
    return iv, np.frombuffer(ciphertext, dtype=np.uint8)

def get_hash(image: np.ndarray, length=64) -> np.ndarray:
    sha256 = hashlib.sha256(image).digest()
    return np.frombuffer(sha256[:length], dtype=np.uint8)

def embed_svd(frame: np.ndarray, data: np.ndarray, alpha=0.05) -> np.ndarray:
    U, S, Vt = np.linalg.svd(frame.astype(np.float64), full_matrices=False)
    length = min(len(S), len(data))
    S[:length] += alpha * data[:length]
    watermarked = np.dot(U, np.dot(np.diag(S), Vt))
    return np.clip(watermarked, 0, 255).astype(np.uint8)

def embed_watermark(video_path, watermark_path, output_dir, alpha=0.05):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'output.mp4')
    cipher_path = os.path.join(output_dir, 'cipher.bin')
    meta_path = os.path.join(output_dir, 'embed_meta.npz')

    cap = cv2.VideoCapture(video_path)
    frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height), isColor=False)

    wm = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)
    if wm is None:
        raise ValueError(f"❌ Gagal membaca watermark: {watermark_path}")
    
    key = get_random_bytes(16)
    iv, cipher = encrypt_image_aes(wm, key)

    with open(cipher_path, 'wb') as f:
        f.write(cipher)

    hash_vector = get_hash(wm)

    frame_idx = 0
    original_frame = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if frame_idx == 0:
            original_frame = gray.copy()
            watermarked = embed_svd(gray, hash_vector, alpha)
        else:
            watermarked = gray

        out.write(watermarked)
        frame_idx += 1

    cap.release()
    out.release()

    np.savez(meta_path, key=key, iv=iv, shape=wm.shape, original_frame=original_frame, hash_vector=hash_vector)

    return output_path, cipher_path, meta_path
