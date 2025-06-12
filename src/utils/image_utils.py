import cv2
import numpy as np
from src.utils.logger import default_logger


def resize_image(image, target_size=(128, 128)):
    """Resize image to target size while maintaining aspect ratio."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        return cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
    except Exception as e:
        default_logger.error(f"Error resizing image: {str(e)}")
        raise


def convert_to_grayscale(image):
    """Convert image to grayscale."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        default_logger.error(f"Error converting to grayscale: {str(e)}")
        raise


def enhance_contrast(image):
    """Enhance image contrast using CLAHE."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)
    except Exception as e:
        default_logger.error(f"Error enhancing contrast: {str(e)}")
        raise


def apply_gaussian_blur(image, kernel_size=(9, 9)):
    """Apply Gaussian blur to the image."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        return cv2.GaussianBlur(image, kernel_size, 0)
    except Exception as e:
        default_logger.error(f"Error applying Gaussian blur: {str(e)}")
        raise


def apply_adaptive_threshold(image, block_size=11, c=2):
    """Apply adaptive thresholding to the image."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        return cv2.adaptiveThreshold(
            image, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            block_size, 
            c
        )
    except Exception as e:
        default_logger.error(f"Error applying adaptive threshold: {str(e)}")
        raise


def apply_sharpening(image):
    """Apply sharpening filter to the image."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        return cv2.filter2D(image, -1, kernel)
    except Exception as e:
        default_logger.error(f"Error applying sharpening: {str(e)}")
        raise


def detect_edges(image, threshold1=50, threshold2=150):
    """Detect edges in the image using Canny edge detection."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        edges = cv2.Canny(image, threshold1, threshold2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.dilate(edges, kernel, iterations=1)
    except Exception as e:
        default_logger.error(f"Error detecting edges: {str(e)}")
        raise


def extract_cell(image, row, col, cell_size):
    """Extract a cell from the Sudoku grid."""
    try:
        if image is None:
            raise ValueError("Input image is None")
        y_start = row * cell_size
        x_start = col * cell_size
        return image[y_start:y_start + cell_size, x_start:x_start + cell_size]
    except Exception as e:
        default_logger.error(f"Error extracting cell: {str(e)}")
        raise
