import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PADDLE_PDX_LOCAL_FONT_FILE_PATH"] = "assets/fonts/PingFang-SC-Regular.ttf"

import streamlit as st
from app.config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)


def main():
    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    st.switch_page("pages/home.py")


if __name__ == '__main__':
    main()
