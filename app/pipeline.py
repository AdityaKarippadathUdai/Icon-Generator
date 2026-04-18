import cv2
import numpy as np
from PIL import Image


def process_image(image: Image.Image) -> Image.Image:
    """
    Post-process a generated icon for high contrast and clean edges.

    Steps:
        1. Convert to grayscale
        2. Apply binary thresholding (Otsu) for high contrast
        3. Apply Canny edge detection and overlay onto the thresholded image
        4. Return as a PIL Image

    Args:
        image: PIL Image (RGB or RGBA) from Stable Diffusion.

    Returns:
        Processed PIL Image (grayscale).
    """
    # 1. Grayscale
    img_np = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # 2. Binary thresholding — Otsu picks the optimal threshold automatically
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. Canny edge detection, overlaid onto the binary image
    edges = cv2.Canny(binary, threshold1=50, threshold2=150)
    combined = cv2.bitwise_or(binary, edges)

    # 4. Back to PIL
    return Image.fromarray(combined)