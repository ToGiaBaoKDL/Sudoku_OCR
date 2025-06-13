import cv2
import numpy as np
import imutils
from src.utils.logger import default_logger


class ContourDetectionError(Exception):
    """Custom exception for contour detection errors."""
    pass


class ContourDetector:
    """Class for handling contour detection operations."""

    @staticmethod
    def find_contours(image):
        """Find contours in the image."""
        try:
            cnts = cv2.findContours(image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            return sorted(cnts, key=cv2.contourArea, reverse=True)[:20]
        except Exception as e:
            default_logger.error(f"Error finding contours: {str(e)}")
            raise ContourDetectionError(f"Failed to find contours: {str(e)}")

    @staticmethod
    def filter_contours(contours, image_shape, min_area_ratio=0.008, aspect_ratio_range=(0.2, 1.9), edge_ratio_threshold=0.58):
        """Filter contours based on various criteria."""
        try:
            image_area = image_shape[0] * image_shape[1]
            valid_contours = []

            for c in contours:
                # Check area
                area = cv2.contourArea(c)
                if area < image_area * min_area_ratio:
                    continue

                # Check aspect ratio
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = w / float(h)
                if not (aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]):
                    continue

                # Check convexity
                hull = cv2.convexHull(c)
                if not cv2.isContourConvex(hull):
                    continue

                # Check if quadrilateral
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    # Check edge ratio
                    pts = approx.reshape(4, 2)
                    edges = [np.linalg.norm(pts[i] - pts[(i + 1) % 4]) for i in range(4)]
                    edge_ratio = min(edges) / max(edges)
                    if edge_ratio >= edge_ratio_threshold:
                        valid_contours.append(approx)

            return valid_contours
        except Exception as e:
            default_logger.error(f"Error filtering contours: {str(e)}")
            raise ContourDetectionError(f"Failed to filter contours: {str(e)}")
