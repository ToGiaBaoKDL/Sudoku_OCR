import cv2
import imutils
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border

import numpy as np
import re
from sudoku import Sudoku

from paddleocr import PaddleOCR
import pytesseract

from PIL import Image
import time


def find_puzzle_contour(image, debug=False):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply multiple preprocessing techniques to handle different image conditions
    preprocessed_images = []

    # 1. Standard preprocessing
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh1 = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    preprocessed_images.append(cv2.bitwise_not(thresh1))

    # 2. Additional preprocessing with different parameters
    blurred2 = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh2 = cv2.adaptiveThreshold(blurred2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5)
    preprocessed_images.append(cv2.bitwise_not(thresh2))

    # 3. Add contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred3 = cv2.GaussianBlur(enhanced, (9, 9), 0)
    thresh3 = cv2.adaptiveThreshold(blurred3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    preprocessed_images.append(cv2.bitwise_not(thresh3))

    # 4. Canny Edge Detection
    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thick_edges = cv2.dilate(edges, kernel, iterations=1)
    preprocessed_images.append(thick_edges)

    # Try to find the puzzle in each preprocessed image
    for idx, thresh in enumerate(preprocessed_images):
        # Find contours
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

        if debug:
            output = image.copy()
            cv2.drawContours(output, contours, -1, (0, 255, 0), 2)
            # display(Image.fromarray(output))
            cv2.imshow("Contours", cv2.resize(output, (output.shape[1]//2, output.shape[0]//2)))
            cv2.waitKey(0)

        # Initialize puzzle contour
        puzzleCnt = None

        # Loop over the contours
        for c in contours:
            # Calculate contour area and perimeter
            area = cv2.contourArea(c)
            peri = cv2.arcLength(c, True)

            # Filter out very small contours relative to image size
            image_area = image.shape[0] * image.shape[1]
            if area < image_area * 0.012:
                continue

            # Check if the contour is approximately square
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w / float(h)
            if not (0.2 <= aspect_ratio <= 1.9):
                continue

            # Approximate the contour
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # Convex Hull Check
            hull = cv2.convexHull(c)
            if not cv2.isContourConvex(hull):
                continue

            # Check if we have found our puzzle
            if len(approx) == 4:
                # Calculate the lengths of the sides of the quadrilateral
                pts = approx.reshape(4, 2)
                edges = [
                    np.linalg.norm(pts[i] - pts[(i + 1) % 4]) for i in range(4)
                ]
                # print(edges)
                short_edge = min(edges)
                long_edge = max(edges)

                # Calculate the ratio of the short edge to the long edge
                edge_ratio = short_edge / long_edge

                # Ensure the contour is approximately square-like
                if edge_ratio < 0.58:  # Adjust this threshold as needed
                    continue

                puzzleCnt = approx
                break

        if puzzleCnt is not None:
            if debug:
                output = image.copy()
                cv2.drawContours(output, [puzzleCnt], -1, (0, 255, 0), 2)
                cv2.imshow("Image contour", cv2.resize(output, (output.shape[1]//2, output.shape[0]//2)))
                cv2.waitKey(0)

            return puzzleCnt

    raise Exception(("Could not find Sudoku puzzle outline. "
                     "Try debugging your thresholding and contour steps."))


def find_puzzle(image, debug=False):
    puzzle_contour = find_puzzle_contour(image, debug)

    # Transform the puzzle
    puzzle = four_point_transform(image, puzzle_contour.reshape(4, 2))
    puzzle = cv2.cvtColor(puzzle, cv2.COLOR_BGR2GRAY)
    puzzle = cv2.resize(puzzle, (3600, 3600))
    warped = four_point_transform(image, puzzle_contour.reshape(4, 2))
    if debug:
        # Show the output warped image
        # display(Image.fromarray(cv2.resize(puzzle, (512, 512))))
        cv2.imshow("Puzzle", cv2.resize(warped, (512, 512)))
        cv2.waitKey(0)
    return puzzle, warped


def get_right_perspective(sudoku_board_gray, sudoku_board_rgb):
    board = cv2.resize(sudoku_board_gray, (512, 512))
    row1 = np.hstack([board, board, board, board, board])
    row2 = np.hstack([board, board, board, board, board])
    row3 = np.hstack([board, board, board, board, board])
    row4 = np.hstack([board, board, board, board, board])
    row5 = np.hstack([board, board, board, board, board])
    combined_board = np.vstack([row1, row2, row3, row4, row5])

    # Default angle to 180 in case of error
    angle = 0
    try:
        osd_data = pytesseract.image_to_osd(Image.fromarray(combined_board))
        angle = int(re.search(r"Orientation in degrees: (\d+)", osd_data).group(1))
    except Exception as e:
        print(f"OSD detection failed: {e}. Defaulting to angle 0.")

    board_rotated_gray = sudoku_board_gray.copy()
    board_rotated_rgb = sudoku_board_rgb.copy()
    # Rotate image
    if angle != 0:
        if angle == 90:
            board_rotated_gray = cv2.rotate(sudoku_board_gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
            board_rotated_rgb = cv2.rotate(sudoku_board_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            board_rotated_gray = cv2.rotate(sudoku_board_gray, cv2.ROTATE_180)
            board_rotated_rgb = cv2.rotate(sudoku_board_rgb, cv2.ROTATE_180)
        elif angle == 270:
            board_rotated_gray = cv2.rotate(sudoku_board_gray, cv2.ROTATE_90_CLOCKWISE)
            board_rotated_rgb = cv2.rotate(sudoku_board_rgb, cv2.ROTATE_90_CLOCKWISE)

    return board_rotated_gray, board_rotated_rgb


def preprocess_board(image):
    # Reduce noise with Gaussian blur
    blurred = cv2.GaussianBlur(image, (9, 9), 0)

    # Enhance contrast to make digits more prominent
    contrast = cv2.convertScaleAbs(blurred, alpha=0.9, beta=0)

    # Apply sharpening kernel to improve digit edges
    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    sharpened = cv2.filter2D(contrast, -1, sharpen_kernel)

    return sharpened


def preprocess_cell(cell):
    """
    Process individual Sudoku cell to isolate and clean the digit.

    Args:
        cell: Single cell image from the Sudoku grid
    Returns:
        Processed cell image with isolated digit
    """
    # Apply Otsu's thresholding to get binary image
    thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Remove border artifacts
    thresh = clear_border(thresh)

    # Smooth the digit shape
    thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

    # Enhance digit thickness
    thresh = cv2.dilate(thresh, None, iterations=1)

    # Find digit contours
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # Return original cell if no contours found
    if len(contours) == 0:
        return cell

    # Get the largest contour (should be the digit)
    c = max(contours, key=cv2.contourArea)

    # Create mask for the digit
    mask = np.zeros(thresh.shape, dtype="uint8")
    cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)

    # Calculate percentage of cell filled by contour
    (h, w) = thresh.shape
    percentFilled = cv2.countNonZero(mask) / float(w * h)

    # Filter out noise (contours that are too small)
    if percentFilled < 0.04:
        return cell

    # Apply mask to get clean digit
    digit = cv2.bitwise_and(thresh, thresh, mask=mask)
    digit = cv2.bitwise_not(digit)

    return digit


def process_sudoku_grid(puzzle, debug=False):
    height, width = puzzle.shape[:2]
    cell_height, cell_width = height // 9, width // 9

    # Create empty array for processed puzzle
    processed_puzzle = np.zeros((height, width), dtype=np.uint8)

    # Process each cell
    for y in range(9):
        for x in range(9):
            # Calculate cell boundaries
            y0, y1 = y * cell_height, (y + 1) * cell_height
            x0, x1 = x * cell_width, (x + 1) * cell_width

            # Extract and process individual cell
            cell = puzzle[y0:y1, x0:x1]
            processed_cell = preprocess_cell(cell)

            # Place processed cell back into grid
            processed_puzzle[y0:y1, x0:x1] = processed_cell

    # Show debug visualization if enabled
    if debug:
        # display(Image.fromarray(processed_puzzle))
        cv2.imshow("Preprocessed puzzle", cv2.resize(processed_puzzle,
                                                     (processed_puzzle.shape[1]//3, processed_puzzle.shape[0]))//3)
        cv2.waitKey(0)

    return processed_puzzle


def extract_angle_orientation(board, result_ocr, padding=5):
    """
    Extracts the angle orientation for each detected text in the OCR result.
    Returns a list of dictionaries containing text and its classification result.
    """
    cls_results = []

    for line in result_ocr:
        for detection in line:
            bbox, (text, score) = detection[0], detection[1]

            # Compute padded bounding box
            x_min, y_min = max(0, int(bbox[0][0]) - padding), max(0, int(bbox[0][1]) - padding)
            x_max, y_max = min(board.shape[1], int(bbox[2][0]) + padding), min(board.shape[0],
                                                                               int(bbox[2][1]) + padding)

            # Crop region of interest (ROI)
            roi = board[y_min:y_max, x_min:x_max]
            
            # Initialize OCR engine
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", rec_batch_num=2, det_db_box_thresh=0.3)
            # Extract classification result for the specific ROI
            cls_result = ocr.ocr(roi, cls=True, det=False, rec=False)

            cls_angle = cls_result[0][0][0] if cls_result else None
            cls_score = cls_result[0][0][1] if cls_result else None
            cls_results.append((text, cls_angle, cls_score))

    return cls_results


def extract_sudoku_digit(sudoku_board, result_ocr):
    height, width = sudoku_board.shape[:2]
    cell_width = width // 9
    cell_height = height // 9
    min_box_area = (cell_width * cell_height) * 0.04  # Set a threshold at 4% of a cell's area
    min_box_height = cell_height * 0.15  # Skip boxes shorter than 15% of a cell's height
    aspect_ratio_threshold = 0.8  # Skip if height/width < 0.8
    
    # Khởi tạo ma trận Sudoku 9x9
    digits = [[0 for _ in range(9)] for _ in range(9)]
    cell_counts = [[0 for _ in range(9)] for _ in range(9)]  # Track bounding box count per cell
    
    for line in result_ocr:
        for bbox, info in line:
            text, score = info
            
            if text in ['S', 's', '$']:  
                text = '5' 
                
            if text in ['了', 'T', '？']:  
                text = '7'
                
            if text in ['l', '|', '!', 'L', '一']:  
                text = '1'
                
            if text in ['B', 'ß', '８']:  
                text = '8'
                
            if text in ['Z', '2', '乙']:  
                text = '2'
                
            if text in ['G', '6', 'b']:  
                text = '6'
                
            if text in ['q', 'g', '９']:  
                text = '9'

            # Calculate bounding box area, width, and height
            x_min, y_min = bbox[0]
            x_max, y_max = bbox[2]
            box_width = x_max - x_min
            box_height = y_max - y_min
            box_area = box_width * box_height

            # Compute the bounding box center
            x_center = int((x_min + x_max) / 2)
            y_center = int((y_min + y_max) / 2)

            # Tìm vị trí hàng, cột tương ứng trên Sudoku board
            row = min(y_center // cell_height, 8)  # Giới hạn tối đa index là 8
            col = min(x_center // cell_width, 8)

            # Increment the cell's bounding box count
            cell_counts[row][col] += 1

            # Skip cells with multiple bounding boxes
            if cell_counts[row][col] > 1:
                digits[row][col] = 0  # Reset to 0 if multiple boxes detected
                continue

            # Ignore bounding boxes that are too small, too narrow, or too short
            if box_area < min_box_area or box_height < min_box_height:
                continue  # Skip this box
                
            # Skip bounding boxes where height-to-width ratio is too small
            if box_height / box_width < aspect_ratio_threshold:
                continue  # Skip this box
                
            number = re.search(r'\d', text)  
            digit = int(number.group()) if number else 0

            digits[row][col] = digit  

    return digits


def ocr_sudoku(sudoku_board, debug=False):
    height, width = sudoku_board.shape[:2]
    cell_width = width // 9
    cell_height = height // 9

    # Initialize OCR engine
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", det_db_box_thresh=0.3, rec_batch_num=2)
    slices = {'horizontal_stride': cell_width, 'vertical_stride': cell_height, 'merge_x_thres': 0.05, 'merge_y_thres': 0.05}
    result_ocr = ocr.ocr(sudoku_board, cls=False, slice=slices)
    result_det = [detection[0] for line in result_ocr for detection in line]
    result_rec = [(sublist[1][0], sublist[1][1]) for group in result_ocr for sublist in group]
    result_cls = extract_angle_orientation(sudoku_board, result_ocr)
    digits = extract_sudoku_digit(sudoku_board, result_ocr)
    
    filtered_cls = [item for item in result_cls if item[2] > 0.68]
    num_zero_angle = sum(1 for item in filtered_cls if '0' in item)
    
    flag = False
    if (len(filtered_cls) == 0) or ((num_zero_angle / len(filtered_cls) < 0.7) or (len(result_det) < 17)):
        # Initialize OCR engine
        ocr = PaddleOCR(use_angle_cls=True, lang="ch", det_db_box_thresh=0.3, rec_batch_num=2)
        sudoku_board = cv2.rotate(sudoku_board, cv2.ROTATE_180)
        result_ocr = ocr.ocr(sudoku_board, cls=False, slice=slices)
        result_det = [detection[0] for line in result_ocr for detection in line]
        result_rec = [(sublist[1][0], sublist[1][1]) for group in result_ocr for sublist in group]
        digits = extract_sudoku_digit(sudoku_board, result_ocr)
        flag = True
            

    # Tạo bảng sudoku
    puzzle = Sudoku(3, 3, digits)

    if debug:
        for line in result_ocr[0]:
            print(line[1])
            
        for box in result_det:
            box = np.array(box).astype(np.int32)
            xmin = min(box[:, 0])
            ymin = min(box[:, 1])
            xmax = max(box[:, 0])
            ymax = max(box[:, 1])

            # Draw bounding box (red color in BGR)
            cv2.rectangle(sudoku_board, (xmin, ymin), (xmax, ymax), (0, 0, 255), 5)

        display(Image.fromarray(cv2.resize(sudoku_board, (512, 512))))

        print("Bài toán Sudoku:")
        puzzle.show()

    return puzzle, flag
    

def solve_sudoku(puzzle):
    solution = puzzle.solve()
    return solution


def insert_answer_2_board(sudoku_board, original_board, solution_board, debug=False):
    final_board = sudoku_board.copy()
    height, width = final_board.shape[:2]
    cell_width = width // 9
    cell_height = height // 9

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(cell_width, cell_height) / 60 + 0.5
    font_thickness = 5
    text_color = (0, 0, 255)

    for row in range(9):
        for col in range(9):
            if original_board[row][col] is None:  # If the cell was empty in the original puzzle
                number = str(solution_board[row][col])

                # Compute text position
                text_size = cv2.getTextSize(number, font, font_scale, font_thickness)[0]
                text_x = col * cell_width + (cell_width - text_size[0]) // 2
                text_y = (row + 1) * cell_height - (cell_height - text_size[1]) // 2

                # Write the number on the board image
                cv2.putText(final_board, number, (text_x, text_y), font, font_scale, text_color, font_thickness)

    if debug:
        cv2.imshow("Final answer", cv2.resize(final_board, (512, 512)))
        cv2.waitKey(0)

    return final_board


def sudoku_pipeline(image, debug_find_puzzle=False, debug_process_grid=False, debug_ocr=False, debug_fill=False, 
                    preprocess=True, process_grid=True, ocr=True, solve=True, fill=True):
    # Bước 1: Tìm bảng Sudoku trong ảnh
    sudoku_board_gray, sudoku_board_rgb = find_puzzle(image, debug=debug_find_puzzle)
    sudoku_board_gray, sudoku_board_rgb = get_right_perspective(sudoku_board_gray, sudoku_board_rgb)

    # Bước 2: Tiền xử lý bảng Sudoku
    if preprocess:
        sudoku_board_gray_clean = preprocess_board(sudoku_board_gray)
    else:
        sudoku_board_gray_clean = sudoku_board_gray

    # Bước 3: Xử lý lưới Sudoku
    if process_grid:
        sudoku_board_gray_clean = process_sudoku_grid(sudoku_board_gray_clean, debug=debug_process_grid)

    # Bước 4: Nhận dạng ký tự (OCR) để lấy bài toán Sudoku
    if ocr:
        puzzle, flag = ocr_sudoku(sudoku_board_gray_clean, debug=debug_ocr)
        if flag:
            sudoku_board_gray = cv2.rotate(sudoku_board_gray, cv2.ROTATE_180)
            sudoku_board_rgb = cv2.rotate(sudoku_board_rgb, cv2.ROTATE_180)
    else:
        puzzle = None

    # Bước 5: Giải bài toán Sudoku
    if solve and puzzle is not None:
        solution = solve_sudoku(puzzle)
    else:
        solution = None
        
    # Bước 6: Điền số trở lại bảng Sudoku gốc
    if fill and solution is not None:
        filled = insert_answer_2_board(sudoku_board_rgb, puzzle.board, solution.board, debug=debug_fill)
    else:
        filled = None

    time.sleep(1)
    # Trả về kết quả
    return {
        'sudoku_board_rgb': sudoku_board_rgb,
        'sudoku_board_gray': sudoku_board_gray,
        'sudoku_board_gray_clean': sudoku_board_gray_clean,
        'puzzle': puzzle,
        'solution': filled
    }


