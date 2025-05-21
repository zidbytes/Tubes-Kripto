# main.py
from embed import encrypt_with_aes, embed_svd_video
from extract import extract_svd_video, decrypt_with_aes
import os
import cv2
from Crypto.Random import get_random_bytes
from datetime import datetime

def generate_output_path(base_path="output", ext="jpg"):
    os.makedirs(base_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_path, f"recovered_{timestamp}.{ext}")

def main():
    img_path = 'Alhamdulillah/Media/input2.png'
    video_path = 'Alhamdulillah/media/input.mp4'
    stego_output_path = generate_output_path(base_path="Alhamdulillah/Output", ext="avi")
    recovered_output_path = generate_output_path(base_path="Alhamdulillah/Output", ext="jpg")

    aes_key = get_random_bytes(16)

    # Enkripsi Gambar
    print("🔐 Mengenkripsi gambar...")
    encrypted_data, nonce, tag = encrypt_with_aes(img_path, aes_key)
    print(f"✅ Gambar terenkripsi ({len(encrypted_data)} byte)")

    # Embed ke dalam video
    print("🎥 Menyisipkan ke video...")
    embed_svd_video(video_path, encrypted_data, stego_output_path)
    print(f"✅ Video stego disimpan: {stego_output_path}")

    # Ekstraksi dari video
    print("🔍 Mengekstrak data dari video...")
    payload_size = len(encrypted_data)
    extracted_data = extract_svd_video(stego_output_path, payload_size)
    print(f"✅ Payload diekstrak: {len(extracted_data)} byte")

    # Dekripsi kembali gambar
    print("🔓 Mendekripsi payload...")
    decrypted_data = decrypt_with_aes(extracted_data, aes_key, nonce, tag)
    with open(recovered_output_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"✅ Gambar hasil dekripsi disimpan: {recovered_output_path}")

if __name__ == "__main__":
    main()
