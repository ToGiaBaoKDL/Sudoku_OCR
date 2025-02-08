from sudoku_utility import *
from datetime import datetime as dt
import streamlit as st
import time


if __name__ == '__main__':
    start = dt.now()
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Set full-screen layout and page title
    st.set_page_config(page_title="Sudoku Solver", layout="wide")

    # Add a stylish header
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>🧩 Sudoku Solver</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and let AI "
        "solve it! 😊</p>",
        unsafe_allow_html=True)

    # Sidebar with instructions
    st.sidebar.markdown(
        f"""
        <div style="margin: 10px; padding:10px; border-radius:10px; border: 2px solid pink; text-align: center;">
            <h2 style='color: pink;'>📤 Upload Your Sudoku Image</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.sidebar.button("🔄 Restart Solver"):
        st.rerun()

    input_image = st.sidebar.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

    # Create columns for better layout (Original Image | Processed Results)
    col1, col2 = st.columns([2.3, 2.1])

    if input_image is not None:
        image = Image.open(input_image)
        image = np.array(image)

        # Display uploaded image
        col1.markdown("### 📷 Uploaded Image")
        col1.image(image, use_container_width=True)

        # Add a progress bar while processing
        progress_bar = st.progress(0)
        with st.spinner("🛠 Processing the Sudoku puzzle..."):
            try:
                sudoku_result = sudoku_pipeline(image,
                                                debug_find_puzzle=False,
                                                debug_process_grid=False,
                                                debug_ocr=False,
                                                debug_fill=False,
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

