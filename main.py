import sys, base64, cv2, numpy as np, pywt
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QMessageBox, QLabel, QVBoxLayout, QWidget)
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class StegoRSA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganografi DWT-DCT dengan RSA (Tanpa AES)")
        self.setGeometry(100, 100, 420, 350)

        layout = QVBoxLayout()
        self.status = QLabel("Status: Siap")
        layout.addWidget(self.status)

        btns = [
            ("1. Masukkan Gambar", self.load_image),
            ("2. Masukkan Video", self.load_video),
            ("3. Enkripsi Base64 dengan RSA", self.encrypt),
            ("4. Sisipkan Pesan", self.embed),
            ("5. Ekstrak & Dekripsi", self.decrypt)
        ]
        for t, f in btns:
            b = QPushButton(t)
            b.clicked.connect(f)
            layout.addWidget(b)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_path = None
        self.video_path = None
        self.encrypted_data = None
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar")
        if path:
            im = Image.open(path).convert("RGB").resize((8, 8))
            im.save("resized_input.png")
            with open("resized_input.png", "rb") as f:
                self.image_b64 = base64.b64encode(f.read())
            self.status.setText("Gambar dikonversi ke base64 (ukuran kecil).")

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Video")
        if path:
            self.video_path = path
            self.status.setText("Video dimuat.")

    def encrypt(self):
        if not hasattr(self, 'image_b64'):
            self.status.setText("Gambar belum dimuat.")
            return
        try:
            cipher = PKCS1_OAEP.new(self.public_key)
            self.encrypted_data = cipher.encrypt(self.image_b64)
            self.status.setText("Base64 gambar berhasil dienkripsi RSA.")
        except ValueError as e:
            self.status.setText(f"Error: {str(e)}")

    def embed(self):
        if not self.encrypted_data or not self.video_path:
            self.status.setText("Data atau video belum lengkap.")
            return

        bitstream = ''.join(format(byte, '08b') for byte in self.encrypted_data)
        cap = cv2.VideoCapture(self.video_path)
        ret, frame = cap.read()
        if not ret:
            self.status.setText("Gagal baca frame pertama.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        coeffs = pywt.dwt2(gray, 'haar')
        LL, (LH, HL, HH) = coeffs
        dct = cv2.dct(np.float32(HL))
        flat = dct.flatten()
        for i in range(len(bitstream)):
            flat[i] = int(flat[i]) & ~1 | int(bitstream[i])
        HL_mod = cv2.idct(flat.reshape(dct.shape))
        coeffs_mod = LL, (LH, HL_mod, HH)
        new_gray = pywt.idwt2(coeffs_mod, 'haar')
        frame[:, :, 0] = np.uint8(new_gray)

        h, w = frame.shape[:2]
        out = cv2.VideoWriter("video_stego.avi", cv2.VideoWriter_fourcc(*"XVID"), 24, (w, h))
        out.write(frame)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()
        out.release()
        self.status.setText("Penyisipan selesai: video_stego.avi")

    def decrypt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Video Stego")
        if not path:
            return
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        if not ret:
            self.status.setText("Gagal membaca frame.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, (_, HL, _) = pywt.dwt2(gray, 'haar')
        dct = cv2.dct(np.float32(HL)).flatten()
        bits = [str(int(v) & 1) for v in dct[:2048]]  # ~256 byte max
        byte_array = bytearray()
        for i in range(0, len(bits), 8):
            byte_array.append(int(''.join(bits[i:i+8]), 2))

        try:
            cipher = PKCS1_OAEP.new(self.private_key)
            decrypted = cipher.decrypt(bytes(byte_array))
            image_bytes = base64.b64decode(decrypted)
            with open("extracted_image.png", "wb") as f:
                f.write(image_bytes)
            self.status.setText("Gambar berhasil diekstrak dan didekripsi: extracted_image.png")
        except Exception as e:
            self.status.setText(f"Gagal dekripsi: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = StegoRSA()
    win.show()
    sys.exit(app.exec())