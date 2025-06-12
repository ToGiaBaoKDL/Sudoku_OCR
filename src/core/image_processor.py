import cv2
from picwish import PicWish
from imutils.perspective import four_point_transform
from src.utils.logger import default_logger
from .image_preprocessor import ImagePreprocessor, ImagePreprocessingError
from .contour_detector import ContourDetector, ContourDetectionError
from .cell_processor import CellProcessor


class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass


class ImageProcessor:
    """Main class for handling all image processing operations."""

    def __init__(self):
        """Initialize the image processor with required components."""
        self.preprocessor = ImagePreprocessor()
        self.contour_detector = ContourDetector()
        self.cell_processor = CellProcessor(self.preprocessor)

    def find_puzzle_contour(self, image):
        """Find the contour of the Sudoku puzzle in the image."""
        try:
            if image is None:
                raise ImageProcessingError("Input image is None")

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            default_logger.debug("Converted image to grayscale")

            # Apply multiple preprocessing techniques
            preprocessed_images = []

            # 1. Standard preprocessing
            blurred = self.preprocessor.apply_gaussian_blur(gray)
            thresh1 = self.preprocessor.apply_adaptive_threshold(blurred)
            preprocessed_images.append(cv2.bitwise_not(thresh1))

            # 2. Additional preprocessing
            blurred2 = self.preprocessor.apply_gaussian_blur(gray, (7, 7))
            thresh2 = self.preprocessor.apply_adaptive_threshold(blurred2, 15, 5)
            preprocessed_images.append(cv2.bitwise_not(thresh2))

            # 3. Contrast enhancement
            enhanced = self.preprocessor.enhance_contrast(gray)
            blurred3 = self.preprocessor.apply_gaussian_blur(enhanced)
            thresh3 = self.preprocessor.apply_adaptive_threshold(blurred3)
            preprocessed_images.append(cv2.bitwise_not(thresh3))

            # 4. Edge detection
            edges = self.preprocessor.detect_edges(gray)
            preprocessed_images.append(edges)

            # Try to find the puzzle in each preprocessed image
            for thresh in preprocessed_images:
                contours = self.contour_detector.find_contours(thresh)
                valid_contours = self.contour_detector.filter_contours(contours, image.shape)

                if valid_contours:
                    default_logger.info("Successfully found puzzle contour")
                    return valid_contours[0]

            raise ImageProcessingError("Could not find Sudoku puzzle outline")

        except (ImagePreprocessingError, ContourDetectionError) as e:
            default_logger.error(f"Error in find_puzzle_contour: {str(e)}")
            raise ImageProcessingError(f"Failed to find puzzle contour: {str(e)}")

    def find_puzzle(self, image):
        """Find and transform the Sudoku puzzle in the image."""
        try:
            puzzle_contour = self.find_puzzle_contour(image)
            puzzle = four_point_transform(image, puzzle_contour.reshape(4, 2))
            puzzle = cv2.resize(puzzle, (128, 128), interpolation=cv2.INTER_LANCZOS4)
            default_logger.info("Successfully transformed puzzle image")
            return puzzle
        except Exception as e:
            default_logger.error(f"Error in find_puzzle: {str(e)}")
            raise ImageProcessingError(f"Failed to find and transform puzzle: {str(e)}")

    def preprocess_board(self, image):
        """Preprocess the Sudoku board image."""
        try:
            if image is None:
                raise ImageProcessingError("Input image is None")

            blurred = self.preprocessor.apply_gaussian_blur(image)
            contrast = cv2.convertScaleAbs(blurred, alpha=1.1, beta=0)
            sharpened = self.preprocessor.apply_sharpening(contrast)
            default_logger.info("Successfully preprocessed board image")
            return sharpened
        except Exception as e:
            default_logger.error(f"Error in preprocess_board: {str(e)}")
            raise ImageProcessingError(f"Failed to preprocess board: {str(e)}")

    def process_sudoku_grid(self, puzzle_rgb):
        """Process the entire Sudoku grid."""
        try:
            if puzzle_rgb is None:
                raise ImageProcessingError("Input puzzle image is None")

            processed = self.cell_processor.process_grid(puzzle_rgb)
            default_logger.info("Successfully processed entire Sudoku grid")
            return processed
        except Exception as e:
            default_logger.error(f"Error in process_sudoku_grid: {str(e)}")
            raise ImageProcessingError(f"Failed to process Sudoku grid: {str(e)}")

    @staticmethod
    async def enhance_with_picwish(puzzle_rgb):
        cv2.imwrite("sudoku_temp.jpg", cv2.cvtColor(puzzle_rgb, cv2.COLOR_RGB2BGR))
        picwish = PicWish()
        enhanced = await picwish.enhance("sudoku_temp.jpg")
        await enhanced.download("sudoku_enhanced.jpg")
