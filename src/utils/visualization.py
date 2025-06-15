import cv2
from PIL import Image, ImageDraw
from src.utils.logger import default_logger


class VisualizationError(Exception):
    """Custom exception for visualization errors."""
    pass


def draw_solution_on_board(sudoku_board_rgb, original_board, solution_board, ocr_result):
    """Draw the solution on the Sudoku board."""
    try:
        if sudoku_board_rgb is None:
            raise VisualizationError("Input image is None")
        if original_board is None or solution_board is None:
            raise VisualizationError("Board data is None")

        board = sudoku_board_rgb.copy()

        angle = ocr_result['doc_preprocessor_res']['angle']
        if angle == 90:
            board = cv2.rotate(board, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            board = cv2.rotate(board, cv2.ROTATE_180)
        elif angle == 270:
            board = cv2.rotate(board, cv2.ROTATE_90_CLOCKWISE)

        height, width = board.shape[:2]
        cell_width = width // 9
        cell_height = height // 9

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(cell_width, cell_height) / 60 + 0.1
        font_thickness = max(1, int(font_scale * 2))
        text_color = (255, 119, 119)

        for row in range(9):
            for col in range(9):
                if original_board[row][col] is None:
                    number = str(solution_board[row][col])
                    text_size = cv2.getTextSize(number, font, font_scale, font_thickness)[0]
                    text_x = col * cell_width + (cell_width - text_size[0]) // 2
                    text_y = row * cell_height + (cell_height + text_size[1]) // 2
                    cv2.putText(board, number, (text_x, text_y), font, font_scale, text_color, font_thickness)

        default_logger.info("Successfully drew solution on board")
        return board
    except Exception as e:
        default_logger.error(f"Error in draw_solution_on_board: {str(e)}")
        raise VisualizationError(f"Failed to draw solution on board: {str(e)}")


def visualize_paddleocr_result(img_path, result, save_path=None):
    """Visualize PaddleOCR results on the image."""
    try:
        if isinstance(img_path, str):
            image = Image.open(img_path)
        else:
            image = Image.fromarray(img_path)

        angle = result['doc_preprocessor_res']['angle']
        if angle != 0:
            image = image.rotate(angle, expand=True)
        else:
            image = image.copy()

        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)

        rec_texts = result['rec_texts']
        rec_scores = result['rec_scores']
        rec_polys = result['rec_polys']

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

        for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
            if not text or score < 0.5 or not text.isdigit():
                continue

            x_coords = poly[:, 0]
            y_coords = poly[:, 1]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))

            color = colors[i % len(colors)]

            if len(poly) == 4:
                polygon_coords = [(int(poly[j][0]), int(poly[j][1])) for j in range(len(poly))]
                draw.polygon(polygon_coords, outline=color, width=2)
            else:
                draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)

        if save_path:
            draw_img.save(save_path)
            default_logger.info(f"Saved visualization to {save_path}")

        default_logger.info("Successfully created visualization")
        return draw_img
    except Exception as e:
        default_logger.error(f"Error in visualize_paddleocr_result: {str(e)}")
        raise VisualizationError(f"Failed to visualize OCR results: {str(e)}")


def format_sudoku_board(board, box_height=3, box_width=3):
    size = box_height * box_width
    cell_length = len(str(size))
    format_int = '{0:0' + str(cell_length) + 'd}'
    table = ''

    for i, row in enumerate(board):
        if i == 0:
            table += ('+-' + '-' * (cell_length + 1) * box_width) * box_height + '+\n'
        table += (
            ('| ' + '{} ' * box_width) * box_height + '|'
        ).format(*[format_int.format(x) if x is not None and x != 0 else ' ' * cell_length for x in row]) + '\n'
        if i == size - 1 or (i + 1) % box_height == 0:
            table += ('+-' + '-' * (cell_length + 1) * box_width) * box_height + '+\n'
    return table
