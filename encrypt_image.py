import cv2
from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def encrypt_image_hash(image_path, public_key_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image_bytes = image.tobytes()
    image_hash = sha256(image_bytes).digest()

    with open(public_key_path, "rb") as f:
        pubkey = RSA.import_key(f.read())
    cipher = PKCS1_OAEP.new(pubkey)
    encrypted_hash = cipher.encrypt(image_hash)

    with open("encrypted_hash.bin", "wb") as f:
        f.write(encrypted_hash)
    print("✅ Hash gambar berhasil dienkripsi dan disimpan sebagai encrypted_hash.bin")

if __name__ == "__main__":
    encrypt_image_hash("image.jpg", "public.pem")
