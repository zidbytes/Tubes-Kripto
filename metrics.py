import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

def calculate_metrics(original_frame: np.ndarray, watermarked_frame: np.ndarray) -> dict:
    """Calculate quality metrics between original and watermarked frames"""
    
    # 1. Peak Signal-to-Noise Ratio (PSNR)
    psnr_value = psnr(original_frame, watermarked_frame)
    
    # 2. Structural Similarity Index (SSIM)
    ssim_value = ssim(original_frame, watermarked_frame)
    
    # 3. Mean Square Error (MSE)
    mse = np.mean((original_frame - watermarked_frame) ** 2)
    
    # 4. Mean Absolute Error (MAE)
    mae = np.mean(np.abs(original_frame - watermarked_frame))
    
    # 5. Maximum Difference
    max_diff = np.max(np.abs(original_frame - watermarked_frame))
    
    return {
        'psnr': psnr_value,
        'ssim': ssim_value,
        'mse': mse,
        'mae': mae,
        'max_diff': max_diff
    }

def evaluate_video_quality(original_video_path: str, watermarked_video_path: str) -> dict:
    """Evaluate quality metrics for the entire video"""
    
    cap_original = cv2.VideoCapture(original_video_path)
    cap_watermarked = cv2.VideoCapture(watermarked_video_path)
    
    metrics_sum = {
        'psnr': 0,
        'ssim': 0,
        'mse': 0,
        'mae': 0,
        'max_diff': 0
    }
    
    frame_count = 0
    
    while True:
        ret1, frame1 = cap_original.read()
        ret2, frame2 = cap_watermarked.read()
        
        if not ret1 or not ret2:
            break
            
        # Convert to grayscale if not already
        if len(frame1.shape) == 3:
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        if len(frame2.shape) == 3:
            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
        frame_metrics = calculate_metrics(frame1, frame2)
        
        for key in metrics_sum:
            metrics_sum[key] += frame_metrics[key]
            
        frame_count += 1
    
    cap_original.release()
    cap_watermarked.release()
    
    # Calculate averages
    metrics_avg = {
        key: value / frame_count 
        for key, value in metrics_sum.items()
    }
    
    return metrics_avg

def print_evaluation_report(metrics: dict):
    """Print a formatted evaluation report with colors in terminal"""
    # ANSI color codes
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

    print(f"\n{BOLD}=== Video Steganography Quality Report ==={END}")
    print(f"\n{BLUE}Quality Metrics:{END}")
    print(f"{GREEN}✓ PSNR:{END} {metrics['psnr']:.2f} dB")
    print(f"  └─ Higher is better (typical good values: 30-50 dB)")
    
    print(f"\n{GREEN}✓ SSIM:{END} {metrics['ssim']:.4f}")
    print(f"  └─ Closer to 1 is better (>0.95 is excellent)")
    
    print(f"\n{GREEN}✓ MSE:{END} {metrics['mse']:.4f}")
    print(f"  └─ Lower is better (measures average error)")
    
    print(f"\n{GREEN}✓ MAE:{END} {metrics['mae']:.4f}")
    print(f"  └─ Lower is better (average absolute difference)")
    
    print(f"\n{GREEN}✓ Maximum Difference:{END} {metrics['max_diff']:.4f}")
    print(f"  └─ Lower is better (peak error)")
    
    print(f"\n{YELLOW}Summary:{END}")
    quality = "Good" if metrics['psnr'] > 30 and metrics['ssim'] > 0.95 else "Acceptable" if metrics['psnr'] > 20 and metrics['ssim'] > 0.85 else "Poor"
    print(f"Overall Quality: {BOLD}{quality}{END}")
    print(f"\n{BOLD}======================================={END}")