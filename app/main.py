import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os
import traceback
import asyncio
from datetime import datetime as dt

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['FONTCONFIG_PATH'] = '/tmp'
os.environ['FONTCONFIG_FILE'] = '/tmp/fonts.conf'

from src.core.image_processor import ImageProcessor
from src.core.sudoku_solver import SudokuSolver
from src.ocr.paddle_ocr import SudokuOCR
from src.ocr.text_processor import TextProcessor
from src.utils.visualization import draw_solution_on_board
from src.utils.logger import default_logger
from streamlit_paste_button import paste_image_button


# Initialize processors
image_processor = ImageProcessor()
ocr = SudokuOCR()
text_processor = TextProcessor()
sudoku_solver = SudokuSolver()


def process_image(image, has_notes=False, enhance_with_picwish=False):
    """Process the uploaded image and return the solution."""
    try:
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # # Initialize processors
        # status_text.text("Initializing processors...")
        # progress_bar.progress(20)

        # Find and process sudoku board
        status_text.text("Finding and preprocessing the puzzle...")
        sudoku_board_rgb = image_processor.find_puzzle(image)
        sudoku_board_rgb = image_processor.preprocess_board(sudoku_board_rgb)
        sudoku_board_rgb = image_processor.process_sudoku_grid(sudoku_board_rgb)
        progress_bar.progress(40)

        if enhance_with_picwish:
            status_text.text("Enhancing the board with picwish...")
            asyncio.run(image_processor.enhance_with_picwish(sudoku_board_rgb))
            sudoku_board_rgb = cv2.imread("sudoku_enhanced.jpg")
            os.remove("sudoku_enhanced.jpg")
            os.remove("sudoku_temp.jpg")
            progress_bar.progress(60)

        # Run OCR
        status_text.text("Running OCR...")
        ocr_results = ocr.predict(sudoku_board_rgb)
        progress_bar.progress(80)

        # Parse OCR results
        status_text.text("Parsing OCR results...")
        if has_notes:
            sudoku_grid, confidence_scores, ocr_result = text_processor.parse_ocr_results_with_note(
                sudoku_board_rgb,
                ocr_results
            )
        else:
            sudoku_grid, confidence_scores, ocr_result = text_processor.parse_ocr_results(
                sudoku_board_rgb,
                ocr_results
            )
        progress_bar.progress(90)

        # Create and solve the puzzle
        status_text.text("Solving Sudoku puzzle...")
        puzzle = sudoku_solver.create_puzzle(sudoku_grid)
        solved_puzzle = sudoku_solver.solve()

        if any(None in row for row in solved_puzzle.board):
            raise ValueError("Sudoku puzzle could not be solved.")

        # Draw solution on the board
        status_text.text("Drawing solution...")
        solution_image = draw_solution_on_board(
            sudoku_board_rgb, 
            puzzle.board, 
            solved_puzzle.board, 
            ocr_result
        )
        progress_bar.progress(100)
        status_text.text("Processing complete!")

        return {
            'success': True,
            'processed_image': sudoku_board_rgb,
            'solution_image': solution_image,
            'puzzle': puzzle,
            'solution': solved_puzzle
        }

    except Exception as e:
        default_logger.error(f"Error processing image: {str(e)}\n{traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }


def main():
    # Set full-screen layout and page title
    st.set_page_config(page_title="Sudoku Solver", layout="wide")

    # Stylish Header
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>🧩 Sudoku Solver</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and"
        " we'll try to solve it for you! 😊</p>",
        unsafe_allow_html=True)

    # Sidebar Information
    st.sidebar.markdown("## ℹ️ About This Project")
    st.sidebar.info("This project is an OCR-based Sudoku solver that leverages PaddleOCR and OpenCV "
                    "for image processing. It extracts numbers from a Sudoku puzzle image, solves the puzzle, "
                    "and returns the completed Sudoku board.")

    # Image Upload Section
    st.sidebar.markdown("### 📤 Upload or Paste Sudoku Image")
    st.sidebar.write("You can either upload an image file or paste an image from the clipboard.")
    input_image = st.sidebar.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

    col_paste, col_restart = st.columns([0.25, 1])
    with col_paste:
        paste_result = paste_image_button(
            label="🎨 Paste an Image",
            text_color="black",
            background_color="#81C784",
            hover_background_color="#66A76F",
        )
    with col_restart:
        if st.button("🔄 Restart Solver", key="restart_solver", help="Click to reset the solver", type="secondary"):
            st.session_state["processing_started"] = False  # Reset processing state
            st.rerun()

    # Processing Options
    st.markdown("#### ⚙️ Processing Options")
    # First option: Enhance image with PicWish
    setting_col_1_1, setting_col_1_2 = st.columns([0.7, 1])
    with setting_col_1_1:
        enhance_with_picwish = st.checkbox("Enable Image Enhancement with PicWish", value=False)

    with setting_col_1_2:
        with st.expander("🔧 Enhance Image with PicWish?"):
            st.markdown(
                "✔️ **What it does:** Applies advanced image enhancement techniques using PicWish to improve image clarity before processing.\n\n"
                "🔹 **Pros:** Enhances visibility of numbers, potentially improving OCR accuracy, especially for low-quality or noisy images.\n\n"
                "⚠️ **Cons:** May increase processing time and may not be effective for images with complex backgrounds or severe distortions."
            )

    # Second option: Sudoku image contains notes
    setting_col_2_1, setting_col_2_2 = st.columns([0.7, 1])
    with setting_col_2_1:
        has_notes = st.checkbox("Sudoku Image Contains Notes", value=False)

    with setting_col_2_2:
        with st.expander("🔧 Sudoku Image Contains Notes On Grid?"):
            st.markdown(
                "✔️ **What it does:** Processes the Sudoku image while accounting for small numbers (notes) written in cells, typically used as candidate numbers.\n\n"
                "🔹 **Pros:** Ignores small candidate numbers to focus on primary digits, improving grid extraction accuracy.\n\n"
                "⚠️ **Cons:** It takes a considerable amount of time to process the Sudoku board."
            )

    # Handle image input source: either upload or paste
    uploaded_image = input_image is not None
    pasted_image = paste_result.image_data is not None

    if uploaded_image and pasted_image:
        st.warning("⚠️ Both an uploaded image and a pasted image detected. The uploaded image will be used.")
        image_source = input_image  # Prioritize uploaded file
    elif uploaded_image:
        image_source = input_image
    elif pasted_image:
        image_source = paste_result.image_data
    else:
        image_source = None

    # Reset processing state when a new image is uploaded/pasted
    if image_source is not None and "last_image_source" in st.session_state and st.session_state["last_image_source"] != image_source:
        st.session_state["processing_started"] = False  # Reset state when new image is detected
    st.session_state["last_image_source"] = image_source  # Save current image source

    # Display Image if Available
    if image_source is not None:
        if uploaded_image:
            image = Image.open(image_source)  # Open uploaded file
        else:
            image = image_source  # Pasted image is already an image

        image = np.array(image)  # Convert to numpy array

        # Start Button for Processing (Hidden After Click)
        if "processing_started" not in st.session_state:
            st.session_state["processing_started"] = False  # Initialize state

        if not st.session_state["processing_started"]:
            if st.button("▶️ Start Processing", key="start_processing", help="Click to begin solving"):
                st.session_state["processing_started"] = True  # Set processing state
                st.rerun()  # Rerun to hide the button immediately

        # Layout Columns (Original Image | Processed Results)
        col1, col2, col3 = st.columns([1, 0.8, 0.7])

        # Display the Uploaded/Pasted Image
        col1.markdown("#### 📷 Uploaded Image")
        col1.image(image, use_container_width=True)

        if st.session_state["processing_started"]:  # Run processing only if button was clicked
            start = dt.now()  # Start timer

            try:
                # Process the image with selected options
                result = process_image(image, has_notes, enhance_with_picwish)

                if result['success']:
                    # Display Processing Time
                    processing_time = (dt.now() - start).seconds
                    st.write(f"⏳ Processing Time: {processing_time} seconds")

                    # # Display Processed Results
                    col2.markdown("#### ✅ Solved Sudoku")
                    col2.image(result['solution_image'], use_container_width=True)

                    # Display the original puzzle and solution
                    col3.markdown("#### 📝 Original Puzzle")
                    col3.write(result['puzzle'])

                    # Show celebration balloons
                    st.balloons()
                else:
                    col2.markdown("#### ❌ Failed")
                    col2.error(f"Error processing the image: {result['error']}")
                    fail_image = Image.open("src/assets/fail_sudoku.png")
                    col3.markdown(
                        """
                        <h4 style="background: linear-gradient(90deg, #ff6a00, #ee0979); 
                                    -webkit-background-clip: text; 
                                    -webkit-text-fill-color: transparent;">
                            がんばれ 💪
                        </h4>
                        """,
                        unsafe_allow_html=True
                    )
                    col3.image(fail_image, use_container_width=True)

            except Exception as e:
                st.error(
                    f"❌ Unable to recognize or solve the Sudoku puzzle. "
                    f"An error occurred while processing the image: {str(e)}")
                st.info("😭 Please ensure the image is clear and contains a proper Sudoku grid.")

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
