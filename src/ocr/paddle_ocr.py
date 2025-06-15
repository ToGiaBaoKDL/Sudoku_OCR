import os

os.environ["PADDLE_PDX_LOCAL_FONT_FILE_PATH"] = "assets/fonts/PingFang-SC-Regular.ttf"

from paddleocr import PaddleOCR
from src.utils.logger import default_logger


class OCRError(Exception):
    """Custom exception for OCR errors."""
    pass


class SudokuOCR:
    """Class for handling OCR operations for Sudoku puzzles."""
    
    def __init__(self):
        """Initialize the OCR system."""
        try:
            self.ocr = PaddleOCR(
                text_detection_model_name="PP-OCRv5_server_det",
                text_recognition_model_name="PP-OCRv5_server_rec",
                use_doc_orientation_classify=True,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            self.results = None
            default_logger.info("Successfully initialized PaddleOCR")
        except Exception as e:
            default_logger.error(f"Error initializing PaddleOCR: {str(e)}")
            raise OCRError(f"Failed to initialize PaddleOCR: {str(e)}")

    def predict(self, image):
        """Run OCR prediction on the image."""
        try:
            if image is None:
                raise OCRError("Input image is None")

            self.results = self.ocr.predict(
                image,
                use_doc_orientation_classify=True
            )
            default_logger.info("Successfully completed OCR prediction")
            return self.results
        except Exception as e:
            default_logger.error(f"Error in OCR prediction: {str(e)}")
            raise OCRError(f"Failed to perform OCR prediction: {str(e)}")

    def get_results(self):
        """Get the current OCR results."""
        return self.results
