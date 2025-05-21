# stegano/dwt_dct.py
import cv2, numpy as np, pywt

def embed_dwt_dct(video_path, encrypted_bytes, alpha=0.001):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if not success:
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    coeffs = pywt.dwt2(gray, 'haar')
    LL, (LH, HL, HH) = coeffs
    dct = cv2.dct(np.float32(HL))

    # Normalisasi data rahasia sebelum penyisipan
    encrypted_data = np.array(encrypted_bytes, dtype=np.float32)
    encrypted_data_scaled = encrypted_data * alpha

    # Konversi data rahasia ke bentuk biner
    data_bits = ''.join(format(byte, '08b') for byte in encrypted_data_scaled.astype(np.uint8))
    flat_dct = dct.flatten()

    # Simpan panjang data rahasia
    data_length = len(data_bits)

    # Menyisipkan data ke dalam subband HL
    for i in range(min(len(flat_dct), data_length)):
        flat_dct[i] = int(flat_dct[i]) & ~1 | int(data_bits[i])

    # Rekonstruksi subband HL
    dct_mod = flat_dct.reshape(dct.shape)
    HL_mod = cv2.idct(dct_mod)

    # Menggabungkan kembali subband-modified ke dalam koefisien DWT
    coeffs_mod = LL, (LH, HL_mod, HH)
    stego_gray = pywt.idwt2(coeffs_mod, 'haar')
    stego_gray = np.uint8(stego_gray)
    frame[:, :, 0] = stego_gray

    out = cv2.VideoWriter("video_stego.avi", cv2.VideoWriter_fourcc(*"XVID"), 25, (frame.shape[1], frame.shape[0]))
    out.write(frame)

    while True:
        success, frame = cap.read()
        if not success:
            break
        out.write(frame)

    cap.release()
    out.release()
    return True

def extract_dwt_dct(video_path, bit_len):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if not success:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, (_, HL, _) = pywt.dwt2(gray, 'haar')
    dct = cv2.dct(np.float32(HL))
    flat_dct = dct.flatten()
    bits = [str(int(flat_dct[i]) & 1) for i in range(bit_len)]

    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        byte_array.append(int(''.join(byte), 2))

    return bytes(byte_array)