import os
import sys

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from app.config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

from streamlit_option_menu import option_menu
from app.components.styles import gradient_heading
from app.components.styles import apply_global_styles, apply_navibar_styles


def main():
    apply_global_styles()

    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Home", "Sudoku Solver", "Rules", "About"],
            icons=["house", "puzzle", "book", "info-circle"],
            default_index=["Home", "Sudoku Solver", "Rules", "About"].index(st.session_state.current_page),
            orientation="horizontal",
            styles=apply_navibar_styles,
            key="nav_home",
        )

    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.switch_page(f"pages/{selected.lower().replace(' ', '_')}.py")

    st.markdown(gradient_heading("Welcome to Sudoku Solver", 1, "🧩"), unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: #c084fc;'>An AI-powered tool to solve Sudoku puzzles from images!</p>",
        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.container():
        st.markdown(gradient_heading("About the App", 2, "ℹ️", align='left'), unsafe_allow_html=True)
        st.write("""
        Our **Sudoku Solver** uses PaddleOCR and OpenCV to extract and solve Sudoku puzzles from images. 
        Upload or paste an image of a Sudoku grid, and let our app do the rest! Whether you're stuck on a puzzle or 
        just want to verify your solution, we're here to help.
        """)

    with st.container():
        st.markdown(gradient_heading("Features", 2, "✨", align='left'), unsafe_allow_html=True)
        col1, col2 = st.columns([1, 0.9])
        with col1:
            st.markdown("""
            - **Image Upload & Paste**: Easily upload or paste Sudoku images.
            - **Advanced OCR**: Powered by PaddleOCR for accurate number detection and recognition.
            - **Fast Solving**: Solves sudoku puzzles in seconds using efficient algorithms.
            """)
        with col2:
            st.markdown("""
            - **Image Enhancement**: Optional PicWish enhancement for clearer images.
            - **Notes Handling**: Supports puzzles with candidate notes.
            - **Visual Output**: Displays the solved puzzle overlaid on the original image.
            """)

    with st.container():
        st.markdown(gradient_heading("Get Started", 2, "🚀", align='left'), unsafe_allow_html=True)
        st.write("Head to the **Sudoku Solver** page to upload your puzzle and see the magic happen!")
        col1, col2, col3 = st.columns(3)
        col1.image("assets/sudoku_08.jpg", use_container_width=True)
        col2.image("assets/sudoku_06.jpg", use_container_width=True)
        col3.image("assets/sudoku_13.jpg", use_container_width=True)
        st.markdown(
            """
            <div style="text-align: center; font-size: 16px; font-weight: bold; color: #4B6EA9; margin-top: 0.5rem;">
                Example Sudoku Puzzles
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
