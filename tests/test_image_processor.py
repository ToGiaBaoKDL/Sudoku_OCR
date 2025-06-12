import unittest
import numpy as np
from src.core.image_processor import ImageProcessor
from src.utils.image_utils import (
    resize_image,
    convert_to_grayscale,
    enhance_contrast,
    apply_gaussian_blur,
    apply_adaptive_threshold,
    apply_sharpening,
    detect_edges,
    extract_cell
)


class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.image_processor = ImageProcessor()
        # Create test images
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image[25:75, 25:75] = 255  # Create a white square in the middle
        self.test_gray = np.zeros((100, 100), dtype=np.uint8)
        self.test_gray[25:75, 25:75] = 255

    def test_resize_image(self):
        resized = resize_image(self.test_image, (50, 50))
        self.assertEqual(resized.shape, (50, 50, 3))
        self.assertEqual(resized.dtype, np.uint8)

    def test_convert_to_grayscale(self):
        gray = convert_to_grayscale(self.test_image)
        self.assertEqual(len(gray.shape), 2)
        self.assertEqual(gray.dtype, np.uint8)

    def test_enhance_contrast(self):
        enhanced = enhance_contrast(self.test_gray)
        self.assertEqual(enhanced.shape, self.test_gray.shape)
        self.assertEqual(enhanced.dtype, np.uint8)

    def test_apply_gaussian_blur(self):
        blurred = apply_gaussian_blur(self.test_image)
        self.assertEqual(blurred.shape, self.test_image.shape)
        self.assertEqual(blurred.dtype, np.uint8)

    def test_apply_adaptive_threshold(self):
        thresh = apply_adaptive_threshold(self.test_gray)
        self.assertEqual(thresh.shape, self.test_gray.shape)
        self.assertEqual(thresh.dtype, np.uint8)
        self.assertTrue(np.all(np.logical_or(thresh == 0, thresh == 255)))

    def test_apply_sharpening(self):
        sharpened = apply_sharpening(self.test_image)
        self.assertEqual(sharpened.shape, self.test_image.shape)
        self.assertEqual(sharpened.dtype, np.uint8)

    def test_detect_edges(self):
        edges = detect_edges(self.test_gray)
        self.assertEqual(edges.shape, self.test_gray.shape)
        self.assertEqual(edges.dtype, np.uint8)

    def test_extract_cell(self):
        # Create a 9x9 grid image
        grid_image = np.zeros((90, 90), dtype=np.uint8)
        cell_size = 10
        # Fill a specific cell
        grid_image[20:30, 20:30] = 255
        cell = extract_cell(grid_image, 2, 2, cell_size)
        self.assertEqual(cell.shape, (cell_size, cell_size))
        self.assertEqual(cell.dtype, np.uint8)

    def test_find_puzzle(self):
        # Create a test image with a clear square
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        test_image[50:150, 50:150] = 255
        puzzle = self.image_processor.find_puzzle(test_image)
        self.assertEqual(puzzle.shape, (128, 128, 3))
        self.assertEqual(puzzle.dtype, np.uint8)

    def test_preprocess_board(self):
        processed = self.image_processor.preprocess_board(self.test_image)
        self.assertEqual(processed.shape, self.test_image.shape)
        self.assertEqual(processed.dtype, np.uint8)

    def test_process_sudoku_grid(self):
        # Create a test Sudoku grid image
        grid_image = np.zeros((90, 90, 3), dtype=np.uint8)
        processed = self.image_processor.process_sudoku_grid(grid_image)
        self.assertEqual(processed.shape, grid_image.shape)
        self.assertEqual(processed.dtype, np.uint8)


if __name__ == '__main__':
    unittest.main()
