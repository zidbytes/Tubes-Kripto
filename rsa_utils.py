# rsa_utils.py
import rsa
import base64

def generate_keys():
    return rsa.newkeys(512)

def encrypt_message(message, public_key):
    chunk_size = int(public_key.n.bit_length() / 8) - 11
    encrypted_chunks = []

    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        encrypted_chunk = rsa.encrypt(chunk.encode(), public_key)
        encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode())

    return " ".join(encrypted_chunks)

def decrypt_message(encrypted_message, private_key):
    encrypted_chunks = encrypted_message.split(" ")
    decrypted_chunks = []

    for chunk in encrypted_chunks:
        encrypted_data = base64.b64decode(chunk)
        decrypted_chunk = rsa.decrypt(encrypted_data, private_key).decode()
        decrypted_chunks.append(decrypted_chunk)

    return "".join(decrypted_chunks)

def compress_image(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode()

def decompress_image(compressed_data, output_path):
    decoded_data = base64.b64decode(compressed_data)
    with open(output_path, 'wb') as f:
        f.write(decoded_data)