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

from src.core.image_processor import ImageProcessor
from src.core.sudoku_solver import SudokuSolver
from src.ocr.paddle_ocr import SudokuOCR
from src.ocr.text_processor import TextProcessor
from src.utils.visualization import draw_solution_on_board
from src.utils.logger import default_logger
from streamlit_paste_button import paste_image_button


def gradient_heading(text: str,
                     level: int = 1,
                     emoji: str = "",
                     outside_icon: bool = True,
                     center: bool = False
                     ) -> str:
    """
    Generate an HTML heading (h1-h6) with gradient-styled text and optional emoji.

    Parameters:
    text (str): The main heading text.
    level (int): Heading level from 1 to 6 (default is 1 for <h1>).
    emoji (str): An optional emoji to include with the heading.
    outside_icon (bool): If True, the emoji appears outside the gradient effect.
                         If False, the emoji is styled with the gradient.
    center (bool): Whether to center the heading (adds text-align: center).

    Returns:
    str: A styled HTML string suitable for use in st.markdown(..., unsafe_allow_html=True).
    """
    tag = f"h{level}"
    icon_html = f"<span>{emoji}</span>" if emoji and outside_icon else ""
    gradient_text = f"{emoji} {text}" if emoji and not outside_icon else text
    alignment = "text-align: center;" if center else ""

    return f"""
    <{tag} style="font-weight: 700; letter-spacing: 0.5px; {alignment}">
        {icon_html}
        <span style="background: linear-gradient(90deg, #6b7280, #a5b4fc, #f472b6);
                     -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent;
                     background-clip: text;
                     color: transparent;">
            {gradient_text}
        </span>
    </{tag}>
    """


def process_image(image, has_notes=False, enhance_with_picwish=False):
    """Process the uploaded image and return the solution."""
    puzzle = None
    try:
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Initialize processors
        image_processor = ImageProcessor()
        ocr = SudokuOCR()
        text_processor = TextProcessor()
        sudoku_solver = SudokuSolver()

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
            'error': str(e),
            'puzzle': puzzle,
        }


def main():
    # Set full-screen layout and page title
    st.set_page_config(
        page_title="Sudoku Solver",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="assets/sudoku_favicon.png"
    )

    # Initialize session state variables
    if "restart_counter" not in st.session_state:
        st.session_state.restart_counter = 0
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False
    if "image_processed" not in st.session_state:
        st.session_state.image_processed = None

    # Stylish Header
    st.markdown(gradient_heading("Sudoku Solver", 1, "🧩", center=True), unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and"
        " we'll try to solve it for you! 😊</p>",
        unsafe_allow_html=True)

    # Sidebar Information
    st.sidebar.markdown(gradient_heading("About This Project", 2, "ℹ️"), unsafe_allow_html=True)
    st.sidebar.info("This project is an OCR-based Sudoku solver that leverages PaddleOCR and OpenCV "
                    "for image processing. It extracts numbers from a Sudoku puzzle image, solves the puzzle, "
                    "and returns the completed Sudoku board.")

    # Image Upload Section
    st.sidebar.markdown(gradient_heading("Upload or Paste Sudoku Image", 2, "📤"), unsafe_allow_html=True)
    st.sidebar.write("You can either upload an image file or paste an image from the clipboard.")

    # Use restart_counter as key to force widget reset
    input_image = st.sidebar.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        key=f"uploaded_image_{st.session_state.restart_counter}"
    )

    col_paste, col_restart = st.columns([0.25, 1])
    with col_paste:
        # Use restart_counter as key to force widget reset
        paste_result = paste_image_button(
            label="🎨 Paste an Image",
            text_color="black",
            background_color="linear-gradient(90deg, #6b7280, #a5b4fc, #f472b6)",
            hover_background_color="linear-gradient(90deg, #4b5563, #818cf8, #ec4899)",
            key=f"pasted_image_{st.session_state.restart_counter}",
        )
    with col_restart:
        if st.button("🔄 Restart Solver", key="restart_solver", help="Click to reset the solver", type="secondary"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key != "restart_counter":  # Keep restart_counter to maintain widget keys
                    del st.session_state[key]

            # Increment restart counter to force widget reset
            st.session_state.restart_counter += 1
            st.session_state.processing_started = False
            st.session_state.image_processed = None
            st.rerun()

    # Processing Options
    st.markdown(gradient_heading("Processing Options", 4, "⚙️"), unsafe_allow_html=True)

    # First option: Enhance image with PicWish
    setting_col_1_1, setting_col_1_2 = st.columns([0.7, 1])
    with setting_col_1_1:
        enhance_with_picwish = st.checkbox(
            "Enable Image Enhancement with PicWish",
            value=False,
            key=f"enhance_with_picwish_{st.session_state.restart_counter}"
        )
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
        has_notes = st.checkbox(
            "Sudoku Image Contains Notes",
            value=False,
            key=f"contain_notes_{st.session_state.restart_counter}"
        )
    with setting_col_2_2:
        with st.expander("🔧 Sudoku Image Contains Notes On Grid?"):
            st.markdown(
                "✔️ **What it does:** Processes the Sudoku image while accounting for small numbers (notes) written in cells, typically used as candidate numbers.\n\n"
                "🔹 **Pros:** Ignores small candidate numbers to focus on primary digits, improving grid extraction accuracy.\n\n"
                "⚠️ **Cons:** It takes a considerable amount of time to process the Sudoku board."
            )

    # Handle image input source: either upload or paste
    uploaded_image = input_image is not None
    pasted_image = paste_result.image_data is not None if paste_result else False

    if uploaded_image and pasted_image:
        st.warning("⚠️ Both an uploaded image and a pasted image detected. The uploaded image will be used.")
        image_source = input_image  # Prioritize uploaded file
    elif uploaded_image:
        image_source = input_image
    elif pasted_image:
        image_source = paste_result.image_data
    else:
        image_source = None

    # Display Image if Available
    if image_source is not None:
        if uploaded_image:
            image = Image.open(image_source)  # Open uploaded file
        else:
            image = image_source  # Pasted image is already an image

        image = np.array(image)  # Convert to numpy array

        # Store image in session state to maintain it during processing
        st.session_state.image_processed = image

        # Start Button for Processing (Hidden After Click)
        if not st.session_state.processing_started:
            if st.button("▶️ Start Processing", key=f"start_processing_{st.session_state.restart_counter}",
                         help="Click to begin solving"):
                st.session_state.processing_started = True  # Set processing state
                st.rerun()  # Rerun to hide the button immediately

        # Layout Columns (Original Image | Processed Results)
        col1, col2, col3 = st.columns([0.9, 0.8, 0.8])

        # Display the Uploaded/Pasted Image
        col1.markdown(gradient_heading("Uploaded Image", 4, "📷"), unsafe_allow_html=True)
        col1.image(image, use_container_width=True)

        if st.session_state.processing_started:  # Run processing only if button was clicked
            start = dt.now()  # Start timer

            try:
                # Process the image with selected options
                result = process_image(image, has_notes, enhance_with_picwish)

                if result['success']:
                    # Display Processing Time
                    processing_time = (dt.now() - start).seconds
                    st.write(f"⏳ Processing Time: {processing_time} seconds")

                    # Display Processed Results
                    col2.markdown(gradient_heading("Solved Sudoku", 4, "✅"), unsafe_allow_html=True)
                    col2.image(result['solution_image'], use_container_width=True)

                    # Display the original puzzle and solution
                    col3.markdown(gradient_heading("Original Puzzle", 4, "📝"), unsafe_allow_html=True)
                    col3.write(result['puzzle'])

                    # Show celebration balloons
                    st.balloons()
                else:
                    col2.markdown(gradient_heading("Failed", 4, "❌"), unsafe_allow_html=True)
                    col2.error(f"Error processing the image: {result['error']}")
                    fail_image = Image.open("assets/fail_sudoku.png")
                    col3.markdown(gradient_heading("がんばれ", 4, "💪"), unsafe_allow_html=True)
                    col3.image(fail_image, use_container_width=True)
                st.write(f"{result['puzzle']}")
            except Exception as e:
                st.error(
                    f"❌ Unable to recognize or solve the Sudoku puzzle. "
                    f"An error occurred while processing the image: {str(e)}")
                st.info("😭 Please ensure the image is clear and contains a proper Sudoku grid.")

    # Display stored image if available and no new image is uploaded (for cases where checkboxes trigger rerun)
    elif st.session_state.image_processed is not None and not st.session_state.processing_started:
        # This handles the case where user ticks/unticks checkboxes after restart
        # In this case, we don't want to show the old image
        pass

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
