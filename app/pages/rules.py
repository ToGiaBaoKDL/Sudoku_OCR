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
        st.session_state.current_page = "Rules"

    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Home", "Sudoku Solver", "Rules", "About"],
            icons=["house", "puzzle", "book", "info-circle"],
            default_index=["Home", "Sudoku Solver", "Rules", "About"].index(st.session_state.current_page),
            orientation="horizontal",
            styles=apply_navibar_styles,
            key="nav_rules",
        )

    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.switch_page(f"pages/{selected.lower().replace(' ', '_')}.py")

    st.markdown(gradient_heading("Sudoku Rules", 1, "📜"), unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px; color: #c084fc;'>Learn how to play Sudoku like a pro!</p>",
        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.container():
        st.markdown(gradient_heading("What is Sudoku?", 2, "❓", align='left'), unsafe_allow_html=True)
        st.write("""
        Sudoku is a logic-based number placement puzzle played on a 9x9 grid, divided into nine 3x3 subgrids. 
        The objective is to fill the grid with digits from 1 to 9, following specific rules.
        """)

    with st.container():
        st.markdown(gradient_heading("Rules of Sudoku", 2, "📏", align='left'), unsafe_allow_html=True)
        st.markdown("""
        To solve a Sudoku puzzle, you must follow these rules:
        1. **Each row** must contain all digits from 1 to 9 without repetition.
        2. **Each column** must contain all digits from 1 to 9 without repetition.
        3. **Each 3x3 subgrid** (box) must contain all digits from 1 to 9 without repetition.

        The puzzle starts with some cells filled with numbers (clues). Your task is to fill in the empty cells while 
        adhering to these rules. There is only one correct solution for a standard Sudoku puzzle.
        """)

    with st.container():
        st.markdown(gradient_heading("Tips for Solving", 2, "💡", align='left'), unsafe_allow_html=True)
        col1, col2 = st.columns([1, 0.9])
        with col1:
            st.markdown("""
            - **Start with obvious placements**: Look for rows, columns, or boxes with many clues.
            - **Use pencil marks**: Note possible numbers in empty cells.
            - **Eliminate possibilities**: Use existing numbers to rule out candidates.
            """)
        with col2:
            st.markdown("""
            - **Look for single candidates**: If a cell has only one possible number, place it.
            - **Check for unique numbers**: If a number can only go in one cell in a row/column/box, place it.
            - **Practice regularly**: The more you play, the better you get!
            """)

    with st.container():
        st.markdown(gradient_heading("Try It Out!", 2, "🎮", align='left'), unsafe_allow_html=True)
        st.write(
            "Ready to test your skills? Go to the **Sudoku Solver** page to upload a puzzle and see it solved instantly!")
        # st.image("assets/sudoku_example.png", caption="A Sample Sudoku Grid", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Developed with ❤️ using OpenCV & Streamlit</p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
