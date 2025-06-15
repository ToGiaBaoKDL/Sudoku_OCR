import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    .stMainBlockContainer {
        max-width:58rem;
    }
    .stButton>button {
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.05);
    }
    .stContainer {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        background-color: #f9fafb;
    }
    .stExpander {
        border-radius: 8px;
        margin-bottom: 16px;
    }
    div[data-testid="stHorizontalBlock"] > div {
        margin-bottom: 16px;
    }
    .button-style {
        background: linear-gradient(90deg, #6b7280, #a5b4fc, #f472b6);
        color: white;
        font-weight: 600;
        font-size: 16px;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    button:hover {
        opacity: 0.9 !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)


def gradient_heading(text: str,
                     level: int = 1,
                     emoji: str = "",
                     outside_icon: bool = True,
                     align: str = "center") -> str:
    """
    Generates a gradient heading with customizable alignment and emoji.

    Args:
        text (str): The heading text.
        level (int): HTML heading level (1-6).
        emoji (str): Emoji to add.
        outside_icon (bool): If True, emoji is outside the gradient span.
        align (str): One of 'left', 'center', 'right', 'justify'.

    Returns:
        str: HTML string with gradient heading.
    """
    tag = f"h{level}"
    icon_html = f"<span>{emoji}</span>" if emoji and outside_icon else ""
    gradient_text = f"{emoji} {text}" if emoji and not outside_icon else text

    # Validate and apply text alignment
    align = align.lower()
    if align not in {"left", "center", "right", "justify"}:
        align = "left"
    alignment = f"text-align: {align};"

    return f"""
    <{tag} style="font-weight: 700; letter-spacing: 0.5px; {alignment}">
        {icon_html}
        <span style="background: linear-gradient(90deg, #6b7280, #a5b4fc, #f472b6);
                     -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent;
                     background-clip: text;
                     color: transparent;">
            {gradient_text}
        </span>
    </{tag}>
    """


apply_navibar_styles = {
    "container": {
        "padding": "0!important",
        "background": "linear-gradient(135deg, #a78bfa, #f0abfc, #fcd34d)",
    },
    "nav-link": {
        "font-size": "16px",
        "text-align": "center",
        "margin": "4px 0",
        "color": "#4c1d95",
        "padding": "8px 0",
        "--hover-color": "#e9d5ff",
        "border-radius": "6px",
        "transition": "all 0.3s ease",
    },
    "nav-link-selected": {
        "background": "linear-gradient(90deg, #6366f1, #ec4899)",
        "color": "white",
        "font-weight": "700",
        "border-radius": "6px",
        "filter": "drop-shadow(0 0 1px rgba(255,255,255,0.5))",
    },
    "icon": {
        "color": "white",
        "margin-right": "10px",
        "transition": "transform 0.5s ease-in-out",
        "text-shadow": "0 0 2px rgba(0, 0, 0, 0.5)",
        "filter": "drop-shadow(0 0 1px rgba(0,0,0,0.4))",
    },
}
