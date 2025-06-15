import os
import sys

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

from streamlit_option_menu import option_menu
from app.components.styles import apply_global_styles, apply_navibar_styles, gradient_heading


def main():
    apply_global_styles()

    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "About"

    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Home", "Sudoku Solver", "Rules", "About"],
            icons=["house", "puzzle", "book", "info-circle"],
            default_index=["Home", "Sudoku Solver", "Rules", "About"].index(st.session_state.current_page),
            orientation="horizontal",
            styles=apply_navibar_styles,
            key="nav_about",
        )

    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.switch_page(f"pages/{selected.lower().replace(' ', '_')}.py")

    st.markdown(gradient_heading("About This Project", 1, "ℹ️"), unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: #c084fc;'>Learn more about our Sudoku Solver!</p>",
        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.container():
        st.markdown(gradient_heading("Our Mission", 2, "🎯", align='left'), unsafe_allow_html=True)
        st.write("""
        This project aims to make Sudoku solving accessible and fun by leveraging cutting-edge OCR and image processing 
        technologies. Built with OpenCV, PaddleOCR, and Streamlit, our app provides an intuitive way to solve Sudoku 
        puzzles from images.
        """)

    with st.container():
        st.markdown(gradient_heading("Technologies Used", 2, "🛠️", align='left'), unsafe_allow_html=True)
        st.markdown("""
        - **OpenCV**: For image processing and grid detection.
        - **PaddleOCR**: For accurate text recognition in Sudoku cells.
        - **Streamlit**: For creating an interactive web interface.
        - **Python**: The backbone of our application logic.
        """)

    with st.container():
        st.markdown(gradient_heading("Future Plans", 2, "🚀", align='left'), unsafe_allow_html=True)
        st.write("""
        We plan to enhance the app with features like:
        - Support for different Sudoku variants (e.g., 4x4, 16x16 grids).
        - Interactive puzzle creation and solving.
        - Mobile app integration for on-the-go solving.
        Stay tuned for updates!
        """)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
