import keygen
import encrypt_image
import embed_watermark
import extract_watermark

IMAGE_PATH = r"media/image.png"
VIDEO_INPUT_PATH = r"media/input.mp4"

def main():
    print("Tahap 1: Membuat kunci")
    keygen.generate_keys()

    print("\nTahap 2: Enkripsi citra")
    encrypt_image.encrypt_image_hash(IMAGE_PATH, "public.pem")

    print("\nTahap 3: Sisipkan ke video")
    embed_watermark.embed_watermark(VIDEO_INPUT_PATH, "encrypted_hash.bin", "watermarked.avi")

    print("\nTahap 4: Verifikasi dari video")
    extract_watermark.verify_watermark("watermarked.avi", "image.jpg", "private.pem")

if __name__ == "__main__":
    main()
