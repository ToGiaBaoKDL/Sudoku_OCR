import streamlit as st


def show():
    st.title("About")
    st.write("This application uses PaddleOCR to detect and solve Sudoku puzzles from images.")
    st.write("Features:")
    st.write("- Detect Sudoku puzzles in images")
    st.write("- Extract numbers using PaddleOCR")
    st.write("- Solve Sudoku puzzles")
    st.write("- Visualize solutions")


show()
