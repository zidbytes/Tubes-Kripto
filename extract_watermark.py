import cv2
from utils import extract_bits_dwt_dct
from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def verify_watermark(video_path, image_path, private_key_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Gagal membuka video:", video_path)
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Gagal membaca frame dari video.")
        return

    # Panjang bytes yang di-embed harus diketahui,
    # contoh kita tahu hash RSA 256 bytes (2048-bit RSA)
    num_bytes = 256

    bits = extract_bits_dwt_dct(frame, num_bytes)
    encrypted = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    with open(private_key_path, "rb") as f:
        privkey = RSA.import_key(f.read())
    cipher = PKCS1_OAEP.new(privkey)

    try:
        decrypted_hash = cipher.decrypt(encrypted)
    except Exception as e:
        print("❌ Gagal dekripsi:", e)
        return

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    current_hash = sha256(image.tobytes()).digest()

    if current_hash == decrypted_hash:
        print("✅ Verifikasi BERHASIL: Citra asli.")
    else:
        print("❌ Verifikasi GAGAL: Citra telah dimodifikasi.")

if __name__ == "__main__":
    verify_watermark("watermarked.avi", "image.jpg", "private.pem")
