import cv2
import numpy as np
from src.utils.logger import default_logger


class ImagePreprocessingError(Exception):
    """Custom exception for image preprocessing errors."""
    pass


class ImagePreprocessor:
    """Class for handling image preprocessing operations."""
    
    @staticmethod
    def apply_gaussian_blur(image, kernel_size=(9, 9)):
        """Apply Gaussian blur to the image."""
        try:
            return cv2.GaussianBlur(image, kernel_size, 0)
        except Exception as e:
            default_logger.error(f"Error applying Gaussian blur: {str(e)}")
            raise ImagePreprocessingError(f"Failed to apply Gaussian blur: {str(e)}")

    @staticmethod
    def apply_adaptive_threshold(image, block_size=11, c=2):
        """Apply adaptive thresholding to the image."""
        try:
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
            raise ImagePreprocessingError(f"Failed to apply adaptive threshold: {str(e)}")

    @staticmethod
    def enhance_contrast(image):
        """Enhance image contrast using CLAHE."""
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(image)
        except Exception as e:
            default_logger.error(f"Error enhancing contrast: {str(e)}")
            raise ImagePreprocessingError(f"Failed to enhance contrast: {str(e)}")

    @staticmethod
    def apply_sharpening(image):
        """Apply sharpening filter to the image."""
        try:
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])
            return cv2.filter2D(image, -1, kernel)
        except Exception as e:
            default_logger.error(f"Error applying sharpening: {str(e)}")
            raise ImagePreprocessingError(f"Failed to apply sharpening: {str(e)}")

    @staticmethod
    def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
        """Apply bilateral filter to the image."""
        try:
            return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        except Exception as e:
            default_logger.error(f"Error applying bilateral filter: {str(e)}")
            raise ImagePreprocessingError(f"Failed to apply bilateral filter: {str(e)}")

    @staticmethod
    def detect_edges(image, threshold1=50, threshold2=150):
        """Detect edges in the image using Canny edge detection."""
        try:
            edges = cv2.Canny(image, threshold1, threshold2)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            return cv2.dilate(edges, kernel, iterations=1)
        except Exception as e:
            default_logger.error(f"Error detecting edges: {str(e)}")
            raise ImagePreprocessingError(f"Failed to detect edges: {str(e)}")
