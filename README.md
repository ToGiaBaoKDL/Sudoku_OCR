# 🧩 OCR Sudoku Solver

## 📌 Overview

This project is an **OCR-based Sudoku solver** that leverages **PaddleOCR** and **OpenCV** for image processing. It takes an image of a Sudoku puzzle, extracts the numbers, solves the puzzle, and returns the completed Sudoku board.

## 🚀 Pipeline

1. **Locate the Sudoku Board** 🕵️‍♂️
   - Detects and extracts the Sudoku grid from the input image.
2. **Preprocess the Board & Cells** 🎨
   - Applies image processing techniques (thresholding, resizing, etc.) for better OCR accuracy.
3. **OCR for Digit Recognition** 🔢
   - Uses **PaddleOCR** to detect and recognize digits.
4. **Solve the Puzzle** 🏆
   - Extracts detected numbers, fills in missing values, and computes the solution.
5. **Return the Final Image** 📸
   - Overlays the solved numbers back onto the original board image.

## ⚠️ Known Issues

- ❌ **Handwritten digits** are not recognized accurately.
- ❌ **Blurred images** reduce OCR accuracy.

## 💡 Tips for Best Results

✅ Ensure the **Sudoku board is fully visible** in the image.  
✅ Try to **capture a clear, well-lit image** to improve OCR performance.  
✅ Avoid **angled or distorted views** for better board detection.

## 🛠️ Dependencies

- Python
- OpenCV
- PaddleOCR

## 📌 Usage

To test the application, you can use the provided Streamlit app by running the following command:

```bash
streamlit run app.py
```
