import cv2
from utils import extract_bits_dwt_dct
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def decrypt_only(video_path, private_key_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Gagal membuka video: {video_path}")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Gagal membaca frame dari video.")
        return

    # Sesuaikan ukuran bytes encrypted hash (biasanya 256 untuk RSA 2048-bit)
    num_bytes = 256
    bits = extract_bits_dwt_dct(frame, num_bytes)

    # Debug: cek panjang bit dan sebagian data hex
    print(f"Extracted bits length: {len(bits)} bits")
    encrypted = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    print(f"Encrypted hash length: {len(encrypted)} bytes")
    print(f"Encrypted hash sample (hex): {encrypted[:16].hex()}...")

    with open(private_key_path, "rb") as f:
        privkey = RSA.import_key(f.read())
    cipher = PKCS1_OAEP.new(privkey)

    try:
        decrypted = cipher.decrypt(encrypted)
        print("✅ Dekripsi berhasil. Hash:", decrypted.hex())
    except Exception as e:
        print("❌ Gagal dekripsi:", e)

if __name__ == "__main__":
    decrypt_only("watermarked.avi", "private.pem")
