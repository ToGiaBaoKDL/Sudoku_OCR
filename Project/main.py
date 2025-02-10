from sudoku_utility import *
from datetime import datetime as dt
import streamlit as st
from streamlit_paste_button import paste_image_button


if __name__ == '__main__':
    start = dt.now()
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Set full-screen layout and page title
    st.set_page_config(page_title="Sudoku Solver", layout="wide")

    # Add a stylish header
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>🧩 Sudoku Solver</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and"
        " we’ll try to solve it for you! 😊</p>",
        unsafe_allow_html=True)

    # Sidebar with information and image upload options
    st.sidebar.markdown("## ℹ️ About This Project")
    st.sidebar.info("This project is an OCR-based Sudoku solver that leverages PaddleOCR and OpenCV "
                    "for image processing. It extracts numbers from a Sudoku puzzle image, solves the puzzle, "
                    "and returns the completed Sudoku board.")

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
            st.rerun()

    # Sidebar - Processing Options
    st.markdown("#### ⚙️ Processing Options")

    setting_col1, setting_col2 = st.columns([0.9, 1])
    with setting_col1:
        # Expander for Preprocessing Grid
        with st.expander("🔧 Preprocess Grid Before OCR?"):
            st.markdown(
                "✔️ **What it does:** Enhances grid detection before OCR.\n\n"
                "🔹 **Pros:** Can improve recognition by refining the grid.\n\n"
                "⚠️ **Cons:** Not ideal for blurry images—it may distort details."
            )
        preprocess_grid = st.checkbox("Enable Preprocessing", value=True)

    with setting_col2:
        # Expander for Auto-Detect & Verify Orientation
        with st.expander("🌀 Auto-Detect & Verify Orientation?"):
            st.markdown(
                "️️✔️ **What it does:** Checks and corrects Sudoku board orientation **after OCR**.\n\n"
                "🔹 **Pros:** Ensures better accuracy for rotated or tilted images.\n\n"
                "⚠️ **Cons:** Takes slightly longer to process."
            )
        correct_rotation = st.checkbox("Enable Orientation Verification", value=False)

    # Handle image input source: either upload or paste
    uploaded_image = input_image is not None
    pasted_image = paste_result is not None

    if uploaded_image and pasted_image:
        st.warning("⚠️ Both an uploaded image and a pasted image detected. The uploaded image will be used.")
        image_source = input_image  # Prioritize uploaded file
    elif uploaded_image:
        image_source = input_image
    elif pasted_image:
        image_source = paste_result.image_data
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

        try:
            sudoku_result = sudoku_pipeline(image,
                                            debug_find_puzzle=False,
                                            debug_process_grid=False,
                                            debug_ocr=False,
                                            debug_fill=False,
                                            preprocess=True,
                                            process_grid=preprocess_grid,  # Using user choice
                                            ocr=True,
                                            angle_orientation=correct_rotation,  # Using user choice
                                            solve=True,
                                            fill=True)

            # Display processing time
            processing_time = (dt.now() - start).seconds
            st.write(f"⏳ Processing Time: {processing_time} seconds")

            # Display processed results
            col2.markdown("### 📏 Cropped Sudoku Board")
            col2.image(sudoku_result['sudoku_board_rgb'], use_container_width=True)

            col2.markdown("### ✅ Solved Sudoku")
            col2.image(sudoku_result['solution'], use_container_width=True)
        except Exception as e:
            st.error(
                f"❌ Unable to recognize or solve the Sudoku puzzle. "
                f"An error occurred while processing the image: {str(e)}")
            st.info("😭 Please ensure the image is clear and contains a proper Sudoku grid.")

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)
