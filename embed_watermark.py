import cv2
from utils import embed_bits_dwt_dct

def embed_watermark(video_path, encrypted_hash_path, output_path):
    with open(encrypted_hash_path, "rb") as f:
        encrypted_data = f.read()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Gagal membuka video:", video_path)
        return

    # Ganti codec ke MJPG (lossless-ish)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    fps = cap.get(cv2.CAP_PROP_FPS) or 20  # fallback 20 jika FPS tidak tersedia
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index == 0:
            frame = embed_bits_dwt_dct(frame, encrypted_data)
        out.write(frame)
        frame_index += 1

    cap.release()
    out.release()
    print("✅ Watermark berhasil disisipkan ke video:", output_path)

if __name__ == "__main__":
    embed_watermark("input.mp4", "encrypted_hash.bin", "watermarked.avi")
