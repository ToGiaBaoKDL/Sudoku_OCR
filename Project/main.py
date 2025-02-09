from sudoku_utility import *
from datetime import datetime as dt
import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton
import time

import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"


if __name__ == '__main__':
    start = dt.now()
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Set full-screen layout and page title
    st.set_page_config(page_title="Sudoku Solver", layout="wide")

    # Add a stylish header
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>🧩 Sudoku Solver</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and"
        " we’ll try to solve it for you! 😊</p>",
        unsafe_allow_html=True)

    # Sidebar with information and image upload options
    st.sidebar.markdown("### ℹ️ About This Project")
    st.sidebar.info("This project is an OCR-based Sudoku solver that leverages PaddleOCR and OpenCV "
                    "for image processing. It extracts numbers from a Sudoku puzzle image, solves the puzzle, "
                    "and returns the completed Sudoku board.")

    st.sidebar.markdown("### 📤 Upload or Paste Sudoku Image")
    st.sidebar.write("You can either upload an image file or paste an image from the clipboard.")
    input_image = st.sidebar.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

    paste_result = pbutton(
        label="📋 Paste an image",
        text_color="black",
        background_color="pink",
        hover_background_color="#FF5733",
        errors='raise'
    )

    # Restart Button
    if st.sidebar.button("🔄 Restart Solver"):
        st.rerun()

    # Handle image input source: either upload or paste
    uploaded_image = input_image is not None
    pasted_image = paste_result.image_data is not None

    if uploaded_image and pasted_image:
        st.warning("⚠️ Both an uploaded image and a pasted image detected. The uploaded image will be used.")
        image_source = input_image  # Prioritize uploaded file
    elif uploaded_image:
        image_source = input_image
    elif pasted_image:
        image_source = pasted_image
    else:
        image_source = None

    if image_source is not None:
        if uploaded_image:
            image = Image.open(image_source)  # Uploaded file needs to be opened
        else:
            image = image_source  # Pasted image is already an image

        image = np.array(image)  # Convert to numpy array

        # Create columns for better layout (Original Image | Processed Results)
        col1, col2 = st.columns([2.5, 2])

        # Display uploaded or pasted image
        col1.markdown("### 📷 Uploaded Image")
        col1.image(image, use_container_width=True)

        # Add a progress bar while processing
        progress_bar = st.progress(0)
        with st.spinner("🛠 Processing the Sudoku puzzle..."):
            try:
                sudoku_result = sudoku_pipeline(image,
                                                debug_find_puzzle=True,
                                                debug_process_grid=False,
                                                debug_ocr=True,
                                                debug_fill=True,
                                                preprocess=True,
                                                process_grid=True,
                                                ocr=True,
                                                solve=True,
                                                fill=True)
                for percent in range(100):
                    time.sleep(0.015)
                    progress_bar.progress(percent + 1)

                # Display processing time
                st.write(f"Processing Time: {(dt.now() - start).seconds} seconds")

                # Display processed results
                col2.markdown("### 📏 Cropped Sudoku Board")
                col2.image(sudoku_result['sudoku_board_rgb'], use_container_width=True)

                col2.markdown("### ✅ Solved Sudoku")
                col2.image(sudoku_result['solution'], use_container_width=True)

                # Add beautiful effects after successful solve
                st.balloons()
                st.success("🎉 Sudoku Solved Successfully! 🎉")
            except Exception as e:
                st.error(
                    f"❌ Unable to recognize or solve the Sudoku puzzle. "
                    f"An error occurred while processing the image: {str(e)}")
                st.info("😭 Please ensure the image is clear and contains a proper Sudoku grid.")

        # Remove progress bar after completion
        progress_bar.empty()

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)
