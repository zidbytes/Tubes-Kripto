import cv2
import numpy as np
import pywt
import scipy.fftpack

def embed_bits_dwt_dct(frame, data_bytes):
    """
    Embed data_bytes (binary) into the LSB of DCT coefficients
    of the LL subband after DWT of the grayscale frame.

    Args:
        frame (np.ndarray): Color BGR image frame
        data_bytes (bytes): Data to embed (e.g. encrypted hash)

    Returns:
        frame with watermark embedded (np.ndarray)
    """

    # Convert data to bit string
    bits = ''.join(format(byte, '08b') for byte in data_bytes)
    bit_len = len(bits)

    # Convert to grayscale float32
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Perform 2D Haar DWT on grayscale image
    LL, (LH, HL, HH) = pywt.dwt2(gray, 'haar')

    # Apply 2D DCT on LL subband
    dct_LL = scipy.fftpack.dct(scipy.fftpack.dct(LL.T, norm='ortho').T, norm='ortho')

    # Flatten dct_LL coefficients for linear access
    flat = dct_LL.flatten()

    if bit_len > len(flat):
        raise ValueError(f"Data too large to embed, bits={bit_len} but capacity={len(flat)}")

    # Embed bits into LSB of DCT coefficients (convert to int first)
    for i in range(bit_len):
        coeff = int(flat[i])
        coeff = (coeff & ~1) | int(bits[i])  # set LSB to bit[i]
        flat[i] = coeff

    # Reshape back to original shape
    dct_LL = flat.reshape(dct_LL.shape)

    # Apply inverse DCT on LL subband
    idct_LL = scipy.fftpack.idct(scipy.fftpack.idct(dct_LL.T, norm='ortho').T, norm='ortho')

    # Reconstruct image via inverse DWT
    watermarked = pywt.idwt2((idct_LL, (LH, HL, HH)), 'haar')

    # Clip pixel values to valid range and convert to uint8
    watermarked = np.clip(watermarked, 0, 255).astype(np.uint8)

    # Replace blue channel (channel 0) with watermarked gray image
    frame_copy = frame.copy()
    frame_copy[:, :, 0] = watermarked

    return frame_copy


def extract_bits_dwt_dct(frame, num_bytes):
    """
    Extract embedded bits from the LSB of DCT coefficients
    of the LL subband after DWT of the grayscale frame.

    Args:
        frame (np.ndarray): Color BGR image frame with embedded watermark
        num_bytes (int): Number of bytes to extract

    Returns:
        Extracted bits as a bit string
    """

    # Convert to grayscale float32
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Perform 2D Haar DWT on grayscale image
    LL, (LH, HL, HH) = pywt.dwt2(gray, 'haar')

    # Apply 2D DCT on LL subband
    dct_LL = scipy.fftpack.dct(scipy.fftpack.dct(LL.T, norm='ortho').T, norm='ortho')

    # Flatten coefficients for linear access
    flat = dct_LL.flatten()

    bit_len = num_bytes * 8
    if bit_len > len(flat):
        raise ValueError(f"Requested {bit_len} bits but only {len(flat)} coefficients available")

    bits = []
    for i in range(bit_len):
        bit = int(flat[i]) & 1
        bits.append(str(bit))

    return ''.join(bits)
