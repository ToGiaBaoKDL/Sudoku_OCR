import streamlit as st
from app.config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

import cv2
import numpy as np
from PIL import Image
import os
import traceback
import asyncio
from datetime import datetime as dt
from streamlit_option_menu import option_menu
from src.core.image_processor import ImageProcessor
from src.core.sudoku_solver import SudokuSolver
from src.ocr.paddle_ocr import SudokuOCR
from src.ocr.text_processor import TextProcessor
from src.utils.visualization import draw_solution_on_board
from src.utils.logger import default_logger
from src.utils.visualization import format_sudoku_board
from streamlit_paste_button import paste_image_button
from app.components.styles import apply_global_styles, gradient_heading, apply_navibar_styles


def process_image(image, has_notes=False, enhance_with_picwish=False):
    """Process the uploaded image and return the solution."""
    puzzle = None
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()

        image_processor = ImageProcessor()
        ocr = SudokuOCR()
        text_processor = TextProcessor()
        sudoku_solver = SudokuSolver()

        status_text.text("Finding and preprocessing the puzzle...")
        sudoku_board_rgb = image_processor.find_puzzle(image)
        sudoku_board_rgb = image_processor.preprocess_board(sudoku_board_rgb)
        sudoku_board_rgb = image_processor.process_sudoku_grid(sudoku_board_rgb)
        progress_bar.progress(40)

        if enhance_with_picwish:
            status_text.text("Enhancing the board with PicWish...")
            asyncio.run(image_processor.enhance_with_picwish(sudoku_board_rgb))
            sudoku_board_rgb = cv2.imread("sudoku_enhanced.jpg")
            os.remove("sudoku_enhanced.jpg")
            os.remove("sudoku_temp.jpg")
            progress_bar.progress(60)

        status_text.text("Running OCR...")
        ocr_results = ocr.predict(sudoku_board_rgb)
        progress_bar.progress(80)

        status_text.text("Parsing OCR results...")
        if has_notes:
            sudoku_grid, confidence_scores, ocr_result = text_processor.parse_ocr_results_with_note(
                sudoku_board_rgb, ocr_results
            )
        else:
            sudoku_grid, confidence_scores, ocr_result = text_processor.parse_ocr_results(
                sudoku_board_rgb, ocr_results
            )
        progress_bar.progress(90)

        status_text.text("Solving Sudoku puzzle...")
        puzzle = sudoku_solver.create_puzzle(sudoku_grid)
        solved_puzzle = sudoku_solver.solve()

        if any(None in row for row in solved_puzzle.board):
            raise ValueError("Sudoku puzzle could not be solved.")

        status_text.text("Drawing solution...")
        solution_image = draw_solution_on_board(
            sudoku_board_rgb, puzzle.board, solved_puzzle.board, ocr_result
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
    apply_global_styles()

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Sudoku Solver"
    if "restart_counter" not in st.session_state:
        st.session_state.restart_counter = 0
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False
    if "image_processed" not in st.session_state:
        st.session_state.image_processed = None
    if "solver_result" not in st.session_state:
        st.session_state.solver_result = None
    if "processing_time" not in st.session_state:
        st.session_state.processing_time = None
    if "first_time_balloon" not in st.session_state:
        st.session_state.first_time_balloon = True
    if "image_file" not in st.session_state:
        st.session_state.image_file = None

    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Home", "Sudoku Solver", "Rules", "About"],
            icons=["house", "puzzle", "book", "info-circle"],
            default_index=["Home", "Sudoku Solver", "Rules", "About"].index(st.session_state.current_page),
            orientation="horizontal",
            styles=apply_navibar_styles,
            key="nav_solver",
        )

    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.switch_page(f"pages/{selected.lower().replace(' ', '_')}.py")

    st.markdown(gradient_heading("Sudoku Solver", 1, "🧩"), unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: #c084fc;'>Upload or paste a Sudoku puzzle image to solve it instantly! 😊</p>",
        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    col_1, col_2, col_3 = st.columns([1, 0.09, 1])
    with col_1:
        st.markdown(gradient_heading("Upload or Paste Image", 3, "📤", align='left'), unsafe_allow_html=True)

        input_image = st.file_uploader(
            "Upload an image or paste from clipboard to solve a Sudoku puzzle.",
            type=['png', 'jpg', 'jpeg'],
            key=f"uploaded_image_{st.session_state.restart_counter}_solver"
        )

        col_paste, col_restart = st.columns([0.5, 1])
        with col_paste:
            paste_result = paste_image_button(
                label="🎨 Paste",
                text_color="white",
                background_color="#3498db",
                hover_background_color="#2980b9",
                key=f"pasted_image_{st.session_state.restart_counter}_solver",
            )
        with col_restart:
            if st.button("🔄 Restart", key=f"restart_solver_{st.session_state.restart_counter}", type="secondary"):
                for key in list(st.session_state.keys()):
                    if key not in ["current_page", "restart_counter"]:
                        del st.session_state[key]
                st.session_state.restart_counter += 1
                st.session_state.processing_started = False
                st.session_state.image_processed = None
                st.session_state.solver_result = None
                st.session_state.processing_time = None
                st.rerun()
    with col_3:
        st.markdown(gradient_heading("Options", 3, "⚙️", align='left'), unsafe_allow_html=True)
        with st.container():
            enhance_with_picwish = st.checkbox(
                "Enhance with PicWish",
                value=False,
                key=f"enhance_with_picwish_{st.session_state.restart_counter}_solver"
            )
            with st.expander("🔧 About PicWish Enhancement"):
                st.markdown(
                    "✔️ **Enhances image clarity** for better OCR accuracy.\n\n"
                    "🔹 **Pros:** Improves number detection in low-quality images.\n\n"
                    "⚠️ **Cons:** Increases processing time."
                )

            has_notes = st.checkbox(
                "Contains Notes",
                value=False,
                key=f"contain_notes_{st.session_state.restart_counter}_solver"
            )
            with st.expander("🔧 About Notes"):
                st.markdown(
                    "✔️ **Handles small candidate numbers** in cells.\n\n"
                    "🔹 **Pros:** Ignores notes for accurate grid extraction.\n\n"
                    "⚠️ **Cons:** Slower processing."
                )

    uploaded_image = input_image is not None
    pasted_image = paste_result.image_data is not None if paste_result else False

    if uploaded_image and pasted_image:
        st.warning("⚠️ Both uploaded and pasted images detected. Using uploaded image.")
        image_source = input_image
    elif uploaded_image:
        image_source = input_image
    elif pasted_image:
        image_source = paste_result.image_data
    else:
        image_source = None

    if image_source is not None and not st.session_state.processing_started:
        image = Image.open(image_source) if uploaded_image else image_source
        image = np.array(image)
        st.session_state.image_processed = image
        st.session_state.solver_result = None  # Clear previous results
        st.session_state.processing_time = None
        st.session_state.first_time_balloon = True

        if not st.session_state.processing_started:
            st.markdown("""
                <style>
                div.stButton > button[kind="primary"] {
                    background: linear-gradient(90deg, #6b7280, #a5b4fc, #f472b6);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0.6rem 1.2rem;
                    margin: 0rem 0.5rem;
                    font-size: 16px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
                }

                div.stButton > button[kind="primary"]:hover {
                    filter: brightness(1.1);
                    transform: scale(1.03);
                    cursor: pointer;
                }
                </style>
            """, unsafe_allow_html=True)
            if st.button(
                    "▶️ Solve Puzzle",
                    key=f"start_processing_{st.session_state.restart_counter}_solver",
                    type="primary"
            ):
                st.session_state.processing_started = True
                st.rerun()

    if st.session_state.image_processed is not None:
        col1, col2, col3 = st.columns([1, 0.85, 0.8])
        with col1:
            st.markdown(gradient_heading("Uploaded Image", 4, "📷", align="left"), unsafe_allow_html=True)
            st.image(st.session_state.image_processed, use_container_width=True)

        if st.session_state.processing_started and st.session_state.solver_result is None:
            start = dt.now()
            st.session_state.solver_result = process_image(st.session_state.image_processed, has_notes, enhance_with_picwish)
            st.session_state.processing_time = (dt.now() - start).seconds

        if st.session_state.solver_result is not None:
            result = st.session_state.solver_result
            if result['success']:
                st.write(f"⏳ Processing Time: {st.session_state.processing_time} seconds")
                with col2:
                    st.markdown(gradient_heading("Solved Puzzle", 4, "✅", align="left"), unsafe_allow_html=True)
                    st.image(result['solution_image'], use_container_width=True)
                with col3:
                    st.markdown(gradient_heading("Original Puzzle", 4, "📝", align="left"), unsafe_allow_html=True)
                    sudoku_ascii = format_sudoku_board(result['puzzle'].board)
                    st.code(sudoku_ascii)
                if st.session_state.first_time_balloon:
                    st.balloons()
                    st.session_state.first_time_balloon = False
            else:
                with col2:
                    st.markdown(gradient_heading("Failed", 4, "❌", align="left"), unsafe_allow_html=True)
                    st.error(f"Error: {result['error']}")
                    sudoku_ascii = format_sudoku_board(result['puzzle'].board) if result['puzzle'] else "No puzzle detected"
                    st.code(sudoku_ascii)
                with col3:
                    st.markdown(gradient_heading("Try Again", 4, "💪", align="left"), unsafe_allow_html=True)
                    st.image("assets/fail_sudoku.png", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
