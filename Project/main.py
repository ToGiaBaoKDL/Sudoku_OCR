from sudoku_utility import *
from datetime import datetime as dt
import streamlit as st
from streamlit_paste_button import paste_image_button
import asyncio
from picwish import PicWish
import io


async def enhance_image(img):
    picwish = PicWish()

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')

    # Enhance an image
    enhanced_image = await picwish.enhance(img_bytes.getvalue())

    # Get image data as bytes
    image_bytes = await enhanced_image.get_bytes()
    image_pil = Image.open(io.BytesIO(image_bytes))

    return np.array(image_pil)


if __name__ == '__main__':
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Set full-screen layout and page title
    st.set_page_config(page_title="Sudoku Solver", layout="wide")

    # Stylish Header
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>🧩 Sudoku Solver</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: pink;'>Upload an image of a Sudoku puzzle and"
        " we’ll try to solve it for you! 😊</p>",
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
    setting_col_1_1, setting_col_1_2 = st.columns([0.7, 1])
    with setting_col_1_1:
        sharpened = st.checkbox("Enhance Image for Better Sudoku Grid Detection", value=False)

    with setting_col_1_2:
        with st.expander("🔍 Enhance Image for Grid Detection?"):
            st.markdown(
                "✔️ **What it does:** Applies sharpening techniques to improve contour detection of the Sudoku grid.\n\n"
                "🔹 **Pros:** Sometimes increases accuracy of detecting the grid structure.\n\n"
                "⚠️ **Cons:** Might take more time to process."
            )

    setting_col_2_1, setting_col_2_2 = st.columns([0.7, 1])
    with setting_col_2_1:
        preprocess_grid = st.checkbox("Enable Cells Preprocessing", value=False)

    with setting_col_2_2:
        with st.expander("🔧 Preprocess Cells Before OCR?"):
            st.markdown(
                "✔️ **What it does:** Enhances each cell for better OCR recognition.\n\n"
                "🔹 **Pros:** Can improve accuracy of recognizing numbers.\n\n"
                "⚠️ **Cons:** May not work well for black background images or blurry images."
            )

    setting_col_3_1, setting_col_3_2 = st.columns([0.7, 1])
    with setting_col_3_1:
        correct_rotation = st.checkbox("Enable Orientation Verification", value=False)

    with setting_col_3_2:
        with st.expander("🌀 Auto-Detect & Verify Orientation?"):
            st.markdown(
                "️✔️ **What it does:** Checks and corrects Sudoku board orientation **after OCR**.\n\n"
                "🔹 **Pros:** Ensures better accuracy for rotated or tilted images.\n\n"
                "⚠️ **Cons:** Takes slightly longer to process."
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
        col1, col2 = st.columns([0.95, 1])

        # Display the Uploaded/Pasted Image
        col1.markdown("### 📷 Uploaded Image")
        col1.image(image, use_container_width=True)

        if st.session_state["processing_started"]:  # Run processing only if button was clicked
            start = dt.now()  # Start timer

            if sharpened:
                image = asyncio.run(enhance_image(Image.fromarray(image)))

            try:
                sudoku_result = sudoku_pipeline(image,
                                                debug_find_puzzle=False,
                                                debug_process_grid=False,
                                                debug_ocr=False,
                                                debug_fill=False,
                                                preprocess=True,
                                                process_grid=preprocess_grid,  # User setting
                                                ocr=True,
                                                angle_orientation=correct_rotation,  # User setting
                                                solve=True,
                                                fill=True)

                # Display Processing Time
                processing_time = (dt.now() - start).seconds
                st.write(f"⏳ Processing Time: {processing_time} seconds")

                # Display Processed Results
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
