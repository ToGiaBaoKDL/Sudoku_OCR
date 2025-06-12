from setuptools import setup, find_packages

setup(
    name="sudoku_ocr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "paddlepaddle",
        "paddleocr",
        "opencv-python-headless",
        "opencv-python",
        "numpy",
        "imutils",
        "pillow",
        "scikit-image",
        "py-sudoku",
        "streamlit-paste-button",
    ],
    author="To Gia Bao",
    author_email="baokdl2226@gmail.com",
    description="A Sudoku OCR solver using PaddleOCR",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ToGiaBaoKDL/Sudoku_OCR",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
