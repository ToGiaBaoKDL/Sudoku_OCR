from src.utils.logger import default_logger


class TextProcessingError(Exception):
    """Custom exception for text processing errors."""
    pass


class TextProcessor:
    """Class for processing OCR text results into Sudoku grid."""
    
    def __init__(self):
        """Initialize the text processor."""
        self.sudoku_grid = None
        self.confidence_scores = None
        self.ocr_result = None

    def parse_ocr_results(self, sudoku_board_rgb, ocr_results):
        """Parse OCR results into a Sudoku grid."""
        try:
            if sudoku_board_rgb is None:
                raise TextProcessingError("Input image is None")
            if ocr_results is None:
                raise TextProcessingError("OCR results are None")

            height, width = sudoku_board_rgb.shape[:2]
            cell_height = height // 9
            cell_width = width // 9

            self.sudoku_grid = [[0 for _ in range(9)] for _ in range(9)]
            self.confidence_scores = [[0.0 for _ in range(9)] for _ in range(9)]
            self.ocr_result = ocr_results[0] if ocr_results and ocr_results[0] else {
                'rec_texts': [], 
                'rec_scores': [], 
                'rec_polys': []
            }

            if not ocr_results or not ocr_results[0]:
                default_logger.warning("No OCR results found")
                return self.sudoku_grid, self.confidence_scores, self.ocr_result

            rec_texts = self.ocr_result['rec_texts']
            rec_scores = self.ocr_result['rec_scores']
            rec_polys = self.ocr_result['rec_polys']

            for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
                if not text or score < 0.7:
                    continue

                # Text correction logic
                if text in ['S', 's', '$']:
                    text = '5'
                elif text in ['了', 'T', '？', '?']:
                    text = '7'
                elif text in ['l', '|', '!', 'L', '一', 'I']:
                    text = '1'
                elif text in ['B', 'ß', '８']:
                    text = '8'
                elif text in ['Z', '2', '乙']:
                    text = '2'
                elif text in ['G', '6', 'b']:
                    text = '6'
                elif text in ['q', 'g', '９']:
                    text = '9'

                if not text.isdigit():
                    continue

                x_coords = poly[:, 0]
                y_coords = poly[:, 1]
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))

                x_center = (x_min + x_max) // 2
                y_center = (y_min + y_max) // 2

                row = min(y_center // cell_height, 8)
                col = min(x_center // cell_width, 8)

                if len(text) == 1 and 1 <= int(text) <= 9:
                    self.sudoku_grid[row][col] = int(text)
                    self.confidence_scores[row][col] = score

            default_logger.info("Successfully parsed OCR results into Sudoku grid")
            return self.sudoku_grid, self.confidence_scores, self.ocr_result
        except Exception as e:
            default_logger.error(f"Error in parse_ocr_results: {str(e)}")
            raise TextProcessingError(f"Failed to parse OCR results: {str(e)}")

    def parse_ocr_results_with_note(self, sudoku_board_rgb, ocr_results):
        """Parse OCR results into a Sudoku grid, handling potential notes."""
        try:
            if sudoku_board_rgb is None:
                raise TextProcessingError("Input image is None")
            if ocr_results is None:
                raise TextProcessingError("OCR results are None")

            # Get image dimensions
            height, width = sudoku_board_rgb.shape[:2]
            cell_height = height // 9
            cell_width = width // 9

            # Initialize 9x9 grid for digits and confidence scores
            self.sudoku_grid = [[0 for _ in range(9)] for _ in range(9)]
            self.confidence_scores = [[0.0 for _ in range(9)] for _ in range(9)]
            self.ocr_result = ocr_results[0] if ocr_results and ocr_results[0] else {
                'rec_texts': [],
                'rec_scores': [],
                'rec_polys': []
            }

            if not ocr_results or not ocr_results[0]:
                default_logger.warning("No OCR results found")
                return self.sudoku_grid, self.confidence_scores, self.ocr_result

            # Extract OCR results
            rec_texts = self.ocr_result['rec_texts']
            rec_scores = self.ocr_result['rec_scores']
            rec_polys = self.ocr_result['rec_polys']

            # Dictionary to track bounding boxes per cell
            cell_bboxes = [[[] for _ in range(9)] for _ in range(9)]

            # Assign bounding boxes to cells based on their center
            for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
                # Skip invalid or low-confidence results
                if not text or score < 0.7 or not text.isdigit():
                    continue

                # Get bounding box coordinates
                x_coords = poly[:, 0]
                y_coords = poly[:, 1]
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))

                # Calculate the center of the bounding box
                x_center = (x_min + x_max) // 2
                y_center = (y_min + y_max) // 2

                # Determine the primary cell based on the center
                row = min(y_center // cell_height, 8)  # Ensure within 0-8
                col = min(x_center // cell_width, 8)  # Ensure within 0-8

                # Store bounding box info for this cell
                cell_bboxes[row][col].append({
                    'text': text,
                    'score': score,
                    'poly': poly,
                    'x_min': x_min,
                    'x_max': x_max,
                    'y_min': y_min,
                    'y_max': y_max,
                    'x_center': x_center,
                    'y_center': y_center
                })

            # Process each cell
            for row in range(9):
                for col in range(9):
                    bboxes = cell_bboxes[row][col]

                    # Skip cells with 2 or more bounding boxes (likely notes)
                    if len(bboxes) >= 2:
                        continue

                    # If cell has exactly one bounding box, apply additional checks
                    if len(bboxes) == 1:
                        bbox = bboxes[0]
                        text = bbox['text']
                        score = bbox['score']
                        x_min, x_max = bbox['x_min'], bbox['x_max']
                        y_min, y_max = bbox['y_min'], bbox['y_max']
                        x_center, y_center = bbox['x_center'], bbox['y_center']

                        # Calculate bounding box dimensions
                        bbox_width = x_max - x_min
                        bbox_height = y_max - y_min
                        bbox_area = bbox_width * bbox_height

                        # Calculate cell area
                        cell_area = cell_width * cell_height

                        # Skip if bounding box area is less than 13% of cell area
                        if bbox_area < 0.13 * cell_area:
                            continue

                        # Check if bounding box center is within the central region of the cell
                        if bbox_area < cell_area:
                            padding_ratio = 0.3
                            x_min_cell = col * cell_width
                            x_max_cell = (col + 1) * cell_width
                            y_min_cell = row * cell_height
                            y_max_cell = (row + 1) * cell_height

                            x_center_min = x_min_cell + padding_ratio * cell_width
                            x_center_max = x_max_cell - padding_ratio * cell_width
                            y_center_min = y_min_cell + padding_ratio * cell_height
                            y_center_max = y_max_cell - padding_ratio * cell_height

                            if not (
                                    x_center_min <= x_center <= x_center_max and y_center_min <= y_center <= y_center_max):
                                continue

                        # Handle single-digit case
                        if len(text) == 1 and 1 <= int(text) <= 9:
                            self.sudoku_grid[row][col] = int(text)
                            self.confidence_scores[row][col] = score

                        # Handle multi-digit case (e.g., "62" or "347")
                        elif len(text) > 1:
                            # Calculate which cells the bounding box spans
                            start_col = max(x_min // cell_width, 0)
                            end_col = min((x_max + cell_width - 1) // cell_width, 9)
                            start_row = max(y_min // cell_height, 0)
                            end_row = min((y_max + cell_height - 1) // cell_height, 9)

                            # Split digits across cells (assume horizontal span for now)
                            num_cells = end_col - start_col
                            if num_cells == len(text) and num_cells > 1:
                                # Horizontal span: assign digits left-to-right
                                for i, digit in enumerate(text):
                                    if 1 <= int(digit) <= 9:
                                        col_idx = start_col + i
                                        if col_idx < 9 and row < 9:
                                            self.sudoku_grid[row][col_idx] = int(digit)
                                            self.confidence_scores[row][col_idx] = score
                            elif end_row - start_row == len(text) and len(text) > 1:
                                # Vertical span: assign digits top-to-bottom
                                for i, digit in enumerate(text):
                                    if 1 <= int(digit) <= 9:
                                        row_idx = start_row + i
                                        if row_idx < 9 and col < 9:
                                            self.sudoku_grid[row_idx][col] = int(digit)
                                            self.confidence_scores[row_idx][col] = score

            default_logger.info("Successfully parsed OCR results into Sudoku grid with notes")
            return self.sudoku_grid, self.confidence_scores, self.ocr_result

        except Exception as e:
            default_logger.error(f"Error in parse_sudoku_ocr_has_note: {str(e)}")
            raise TextProcessingError(f"Failed to parse OCR results with notes: {str(e)}")

    def get_sudoku_grid(self):
        """Get the current Sudoku grid."""
        return self.sudoku_grid

    def get_confidence_scores(self):
        """Get the current confidence scores."""
        return self.confidence_scores

    def get_ocr_result(self):
        """Get the current OCR result."""
        return self.ocr_result
