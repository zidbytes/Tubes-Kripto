import rsa
import base64

# 🔐 Generate public-private RSA keys
def generate_keys():
    return rsa.newkeys(512)

# 🔒 Encrypt long message with RSA chunking + base64 encoding
def encrypt_message(message, public_key):
    chunk_size = int(public_key.n.bit_length() / 8) - 11  # Max size for RSA encryption with PKCS1
    encrypted_chunks = []

    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        try:
            encrypted = rsa.encrypt(chunk.encode(), public_key)
            encoded = base64.b64encode(encrypted).decode()
            encrypted_chunks.append(encoded)
        except Exception as e:
            print(f"❌ Gagal mengenkripsi chunk: {e}")

    return "|||".join(encrypted_chunks)  # gunakan pemisah aman

# 🔓 Decrypt base64 + RSA with chunk handling
def decrypt_message(encrypted_message, private_key):
    encrypted_chunks = encrypted_message.split("|||")
    decrypted_chunks = []

    for chunk in encrypted_chunks:
        try:
            encrypted_data = base64.b64decode(chunk)
            decrypted = rsa.decrypt(encrypted_data, private_key).decode()
            decrypted_chunks.append(decrypted)
        except Exception as e:
            print(f"❌ Gagal mendekripsi chunk: {e}")

    return "".join(decrypted_chunks)

# 🗜️ Convert image file to base64 string
def compress_image(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode()

# 🔄 Convert base64 string back to image file
def decompress_image(compressed_data, output_path):
    decoded_data = base64.b64decode(compressed_data)
    with open(output_path, 'wb') as f:
        f.write(decoded_data)
