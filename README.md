# 🧩 OCR Sudoku Solver

[English](README.md) | [Tiếng Việt](README.vi.md)

## 📌 Overview

This project is an **OCR-based Sudoku solver** that leverages **PaddleOCR** and **OpenCV** for image processing. It takes an image of a Sudoku puzzle, extracts the numbers, solves the puzzle, and returns the completed Sudoku board.

![Streamlit demo](https://ik.imagekit.io/baodata2226/imagekit-assets/sudoku_interface.png?updatedAt=1749838157494)

## 🌐 Try It Online
Test the application directly using this link: [🔗 Live Demo](https://sudoku-ocr-tgb.streamlit.app/)

## ▶️ Example

| Input | Output |
|-------|--------|
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240123718.png?updatedAt=1739248180963) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240257816.png?updatedAt=1739248181295) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240456648.png?updatedAt=1739248182220) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240415810.png?updatedAt=1739248181033) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739245027555.png?updatedAt=1739248181507) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739245282917.png?updatedAt=1739248181392) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739241829726.png?updatedAt=1739248181261) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739241887565.png?updatedAt=1739248181162) |

## 🚀 Pipeline

1. **Locate the Sudoku Board** 🕵️‍♂️
   - Uses OpenCV's contour detection to identify and extract the Sudoku grid
   - Implements perspective transformation to correct board orientation
   - Handles various board styles and backgrounds

2. **Preprocess the Board & Cells** 🎨
   - Applies adaptive thresholding for better digit separation
   - Implements noise reduction and image enhancement
   - Optional PicWish enhancement for improved clarity
   - Processes individual cells for optimal OCR input

3. **OCR for Digit Recognition** 🔢
   - Utilizes PaddleOCR for accurate digit detection
   - Supports processing of Sudoku notes (small candidate numbers)
   - Implements confidence scoring for digit recognition

4. **Solve the Puzzle** 🏆
   - Implements backtracking algorithm for Sudoku solving
   - Validates puzzle constraints and rules
   - Provides complete solution with error checking

5. **Return the Final Image** 📸
   - Overlays solved numbers onto original board
   - Maintains original image quality and style
   - Highlights solution numbers for better visibility
   - Preserves original puzzle numbers

## 🛠️ Project Structure

```
Sudoku_OCR/
├── app/                    # Streamlit application
│   ├── main.py            # Entry point
│   ├── components/        # UI components
│   ├── pages/            # Additional pages
│   └── config/           # Configuration files
├── src/                   # Source code
│   ├── core/             # Core processing
│   │   ├── image_processor.py
│   │   ├── sudoku_solver.py
│   │   ├── cell_processor.py
│   │   └── contour_detector.py
│   ├── ocr/              # OCR modules
│   │   ├── paddle_ocr.py
│   │   └── text_processor.py
│   └── utils/            # Utilities
├── notebooks/            # Jupyter notebooks
├── tests/               # Test files
├── assets/             # Static assets
├── logs/               # Log files
├── requirements.txt    # Python dependencies
├── packages.txt       # System dependencies
└── setup.py           # Installation script
```

## ⚠️ Known Issues

- **Handwritten digits** are not recognized accurately
- **Blurred images** reduce OCR accuracy
- **Complex backgrounds** may affect board detection
- **Severely distorted images** may not process correctly

## 💡 Tips for Best Results

- Ensure the **Sudoku board is fully visible** in the image
- Try to **capture a clear, well-lit image** to improve OCR performance
- Avoid **angled or distorted views** for better board detection
- Use **printed or digital Sudoku puzzles** for best results
- Enable **PicWish enhancement** for low-quality images
- Check **Sudoku Image Contains Notes** if your puzzle has candidate numbers

## 🛠️ Dependencies

- Python 3.10+
- OpenCV
- PaddleOCR
- Streamlit
- NumPy
- Pillow
- Picwish

## 📌 Usage

1. **Local Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/ToGiaBaoKDL/Sudoku_OCR.git
   cd Sudoku_OCR

   # Install dependencies
   pip install -r requirements.txt

   # Run the application
   streamlit run app/main.py
   ```

2. **Online Demo**
   - Visit the [Live Demo](https://sudoku-ocr-tgb.streamlit.app/)
   - Upload or paste a Sudoku puzzle image
   - Configure processing options if needed
   - Get your solved puzzle!

## 📝 License

This project is licensed under the GNU General Public License - see the LICENSE file for details.
