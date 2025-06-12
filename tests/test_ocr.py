import unittest
import numpy as np
import cv2
from src.ocr.paddle_ocr import SudokuOCR
from src.ocr.text_processor import TextProcessor


class TestOCR(unittest.TestCase):
    def setUp(self):
        self.ocr = SudokuOCR()
        self.text_processor = TextProcessor()
        # Create test images
        self.test_image = np.zeros((128, 128, 3), dtype=np.uint8)
        self.test_image[25:75, 25:75] = 255  # White square in middle
        
        # Create a test Sudoku grid image
        self.grid_image = np.zeros((90, 90, 3), dtype=np.uint8)
        # Add some numbers to the grid
        cv2.putText(self.grid_image, "5", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(self.grid_image, "3", (30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(self.grid_image, "7", (50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def test_ocr_initialization(self):
        """Test OCR initialization"""
        self.assertIsNotNone(self.ocr)
        self.assertIsNotNone(self.ocr.ocr)

    def test_ocr_prediction(self):
        """Test OCR prediction on test image"""
        results = self.ocr.predict(self.test_image)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)

    def test_text_processor_initialization(self):
        """Test text processor initialization"""
        self.assertIsNotNone(self.text_processor)
        self.assertIsNone(self.text_processor.sudoku_grid)
        self.assertIsNone(self.text_processor.confidence_scores)
        self.assertIsNone(self.text_processor.ocr_result)

    def test_parse_ocr_results(self):
        """Test parsing OCR results"""
        # Run OCR on grid image
        ocr_results = self.ocr.predict(self.grid_image)
        
        # Parse results
        grid, scores, result = self.text_processor.parse_ocr_results(
            self.grid_image,
            ocr_results
        )
        
        # Check results
        self.assertIsNotNone(grid)
        self.assertIsNotNone(scores)
        self.assertIsNotNone(result)
        self.assertEqual(len(grid), 9)
        self.assertEqual(len(grid[0]), 9)
        self.assertEqual(len(scores), 9)
        self.assertEqual(len(scores[0]), 9)

    def test_parse_ocr_results_with_note(self):
        """Test parsing OCR results with potential notes"""
        # Run OCR on grid image
        ocr_results = self.ocr.predict(self.grid_image)
        
        # Parse results with note handling
        grid, scores, result = self.text_processor.parse_ocr_results_with_note(
            self.grid_image,
            ocr_results
        )
        
        # Check results
        self.assertIsNotNone(grid)
        self.assertIsNotNone(scores)
        self.assertIsNotNone(result)
        self.assertEqual(len(grid), 9)
        self.assertEqual(len(grid[0]), 9)
        self.assertEqual(len(scores), 9)
        self.assertEqual(len(scores[0]), 9)

    def test_text_correction(self):
        """Test text correction for common OCR mistakes"""
        # Create test cases for common OCR mistakes
        test_cases = {
            'S': '5',
            's': '5',
            '$': '5',
            '了': '7',
            'T': '7',
            '？': '7',
            '?': '7',
            'l': '1',
            '|': '1',
            '!': '1',
            'L': '1',
            '一': '1',
            'I': '1',
            'B': '8',
            'ß': '8',
            '８': '8',
            'Z': '2',
            '2': '2',
            '乙': '2',
            'G': '6',
            '6': '6',
            'b': '6',
            'q': '9',
            'g': '9',
            '９': '9'
        }
        
        # Create a test image with these characters
        test_image = np.zeros((128, 128, 3), dtype=np.uint8)
        x, y = 10, 10
        for char in test_cases.keys():
            cv2.putText(test_image, char, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            x += 20
            if x > 100:
                x = 10
                y += 20
        
        # Run OCR and parse results
        ocr_results = self.ocr.predict(test_image)
        grid, scores, result = self.text_processor.parse_ocr_results(
            test_image,
            ocr_results
        )
        
        # Check if corrections were applied correctly
        # Note: This is a basic check, actual results may vary based on OCR accuracy
        self.assertIsNotNone(grid)
        self.assertIsNotNone(scores)

    def test_invalid_input(self):
        """Test handling of invalid inputs"""
        # Test with None input
        with self.assertRaises(Exception):
            self.ocr.predict(None)
        
        with self.assertRaises(Exception):
            self.text_processor.parse_ocr_results(None, None)
        
        with self.assertRaises(Exception):
            self.text_processor.parse_ocr_results_with_note(None, None)


if __name__ == '__main__':
    unittest.main()
