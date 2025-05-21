# main_cli.py
import os
import cv2
from rsa_utils import compress_image, encrypt_message, decrypt_message, decompress_image
from dwt_dct_utils import embed_image_in_video, extract_image_from_video
from rsa_utils import generate_keys

def show_menu():
    print("\n=== MENU UTAMA ===")
    print("1. Enkripsi Citra dan Sisipkan ke Video")
    print("2. Ekstrak Citra dari Video")
    print("3. Keluar")

def cli_encrypt_and_embed():
    image_path = input("Masukkan path citra: ")
    video_path = input("Masukkan path video: ")
    output_video = input("Masukkan path output video hasil embedding: ")

    if not os.path.exists(image_path):
        print("❌ Citra tidak ditemukan.")
        return
    if not os.path.exists(video_path):
        print("❌ Video tidak ditemukan.")
        return

    print("🔧 Mengenkripsi citra...")
    pub_key, priv_key = generate_keys()
    compressed = compress_image(image_path)
    encrypted = encrypt_message(compressed, pub_key)

    with open("encrypted_data.bin", "w") as f:
        f.write(encrypted)
    print("✅ Citra berhasil dienkripsi sebagai encrypted_data.bin")

    print("🎥 Menyisipkan citra ke video...")
    embed_image_in_video(video_path, image_path, output_video)
    print(f"✅ Video tersimpan di {output_video}")

def cli_extract_image():
    video_path = input("Masukkan path video: ")
    output_image = input("Masukkan path untuk menyimpan citra ekstraksi: ")

    if not os.path.exists(video_path):
        print("❌ Video tidak ditemukan.")
        return

    print("🔍 Mengekstrak citra dari video...")
    extract_image_from_video(video_path, output_image)

    if os.path.exists(output_image):
        print(f"✅ Citra tersimpan di {output_image}")
        # Tampilkan preview (opsional, jika ada GUI atau imshow support)
        img = cv2.imread(output_image)
        cv2.imshow("Extracted Image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Gagal mengekstrak citra.")

if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("Pilih opsi (1-3): ")

        if choice == "1":
            cli_encrypt_and_embed()
        elif choice == "2":
            cli_extract_image()
        elif choice == "3":
            print("👋 Sampai jumpa!")
            break
        else:
            print("❌ Opsi tidak valid.")