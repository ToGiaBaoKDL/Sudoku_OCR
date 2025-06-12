import numpy as np
from src.utils.logger import default_logger


class CellProcessingError(Exception):
    """Custom exception for cell processing errors."""
    pass


class CellProcessor:
    """Class for handling individual cell processing operations."""

    def __init__(self, preprocessor):
        """Initialize with an image preprocessor instance."""
        self.preprocessor = preprocessor

    def process_cell(self, cell_image):
        """Process a single cell image."""
        try:
            if cell_image is None:
                raise CellProcessingError("Input cell image is None")

            # Apply preprocessing steps
            blurred = self.preprocessor.apply_gaussian_blur(cell_image, (11, 11))
            filtered = self.preprocessor.apply_bilateral_filter(blurred)
            sharpened = self.preprocessor.apply_sharpening(filtered)

            return sharpened
        except Exception as e:
            default_logger.error(f"Error processing cell: {str(e)}")
            raise CellProcessingError(f"Failed to process cell: {str(e)}")

    def process_grid(self, puzzle_image):
        """Process the entire Sudoku grid."""
        try:
            if puzzle_image is None:
                raise CellProcessingError("Input puzzle image is None")

            height, width = puzzle_image.shape[:2]
            cell_height = height // 9
            cell_width = width // 9
            processed = np.ones_like(puzzle_image) * 255

            for y in range(9):
                for x in range(9):
                    y0, y1 = y * cell_height, (y + 1) * cell_height
                    x0, x1 = x * cell_width, (x + 1) * cell_width
                    cell = puzzle_image[y0:y1, x0:x1]
                    processed_cell = self.process_cell(cell)
                    processed[y0:y1, x0:x1] = processed_cell

            default_logger.info("Successfully processed entire Sudoku grid")
            return processed
        except Exception as e:
            default_logger.error(f"Error processing grid: {str(e)}")
            raise CellProcessingError(f"Failed to process grid: {str(e)}")

    # def preprocess_cell(cell):
    #     """
    #     Process individual Sudoku cell to isolate and clean the digit.
    #     """
    #     # Apply Otsu's thresholding to get binary image
    #     thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    #     # Remove border artifacts
    #     thresh = clear_border(thresh)

    #     # Smooth the digit shape
    #     thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

    #     # Enhance digit thickness
    #     thresh = cv2.dilate(thresh, None, iterations=1)

    #     # Find digit contours
    #     contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #     contours = imutils.grab_contours(contours)

    #     # Return original cell if no contours found
    #     if len(contours) == 0:
    #         return cell

    #     # Get the largest contour (should be the digit)
    #     c = max(contours, key=cv2.contourArea)

    #     # Create mask for the digit
    #     mask = np.zeros(thresh.shape, dtype="uint8")
    #     cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)

    #     # Calculate percentage of cell filled by contour
    #     (h, w) = thresh.shape
    #     percentFilled = cv2.countNonZero(mask) / float(w * h)

    #     # Filter out noise (contours that are too small)
    #     if percentFilled < 0.04:
    #         return cell

    #     # Apply mask to get clean digit
    #     digit = cv2.bitwise_and(thresh, thresh, mask=mask)
    #     digit = cv2.bitwise_not(digit)

    #     return digit