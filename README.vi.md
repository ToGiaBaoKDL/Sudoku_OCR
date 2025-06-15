# 🧩 Giải Sudoku bằng OCR

[English](README.md) | [Tiếng Việt](README.vi.md)

## 📌 Tổng quan

Dự án này là một **trình giải Sudoku dựa trên OCR** sử dụng **PaddleOCR** và **OpenCV** để xử lý hình ảnh. Nó nhận vào hình ảnh của một bảng Sudoku, trích xuất các số, giải quyết câu đố và trả về bảng Sudoku đã hoàn thành.

![Streamlit demo](https://ik.imagekit.io/baodata2226/imagekit-assets/sudoku_interface.png?updatedAt=1749838157494)

## 🌐 Thử nghiệm trực tuyến
Thử nghiệm ứng dụng trực tiếp qua link: [🔗 Live Demo](https://sudoku-ocr-tgb.streamlit.app/)

## ▶️ Ví dụ

| Đầu vào | Đầu ra |
|-------|--------|
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240123718.png?updatedAt=1739248180963) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240257816.png?updatedAt=1739248181295) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240456648.png?updatedAt=1739248182220) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739240415810.png?updatedAt=1739248181033) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739245027555.png?updatedAt=1739248181507) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739245282917.png?updatedAt=1739248181392) |
| ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739241829726.png?updatedAt=1739248181261) | ![](https://ik.imagekit.io/baodata2226/imagekit-assets/screenshot_1739241887565.png?updatedAt=1739248181162) |

## 🚀 Quy trình xử lý

1. **Xác định vị trí bảng Sudoku** 🕵️‍♂️
   - Sử dụng phát hiện đường viền của OpenCV để xác định và trích xuất lưới Sudoku
   - Thực hiện biến đổi phối cảnh để điều chỉnh hướng bảng
   - Xử lý nhiều kiểu bảng và nền khác nhau

2. **Tiền xử lý bảng và ô** 🎨
   - Áp dụng ngưỡng thích ứng để tách biệt số tốt hơn
   - Thực hiện giảm nhiễu và cải thiện hình ảnh
   - Tùy chọn cải thiện PicWish để rõ ràng hơn
   - Xử lý từng ô riêng biệt để tối ưu đầu vào OCR

3. **OCR nhận dạng số** 🔢
   - Sử dụng PaddleOCR để phát hiện số chính xác
   - Hỗ trợ xử lý ghi chú Sudoku (số ứng viên nhỏ)
   - Thực hiện tính điểm tin cậy cho nhận dạng số

4. **Giải câu đố** 🏆
   - Thực hiện thuật toán quay lui để giải Sudoku
   - Xác thực các ràng buộc và quy tắc của câu đố
   - Cung cấp giải pháp hoàn chỉnh với kiểm tra lỗi

5. **Trả về hình ảnh cuối cùng** 📸
   - Viết đè các số đã giải ra lên bảng sudoku gốc
   - Duy trì chất lượng và phong cách hình ảnh gốc
   - Làm nổi bật các số giải pháp để dễ nhìn hơn
   - Giữ nguyên các số ở câu đố gốc

## 🛠️ Cấu trúc dự án

```
Sudoku_OCR/
├── app/                    # Ứng dụng Streamlit
│   ├── main.py            # Điểm khởi đầu
│   ├── components/        # Các thành phần giao diện
│   ├── pages/            # Các trang bổ sung
│   └── config/           # Tệp cấu hình
├── src/                   # Mã nguồn
│   ├── core/             # Xử lý cốt lõi
│   │   ├── image_processor.py
│   │   ├── sudoku_solver.py
│   │   ├── cell_processor.py
│   │   └── contour_detector.py
│   ├── ocr/              # Các module OCR
│   │   ├── paddle_ocr.py
│   │   └── text_processor.py
│   └── utils/            # Các tiện ích
├── notebooks/            # Jupyter notebooks
├── tests/               # Tệp kiểm thử
├── assets/             # Tài nguyên tĩnh
├── logs/               # Tệp nhật ký
├── requirements.txt    # Phụ thuộc Python
├── packages.txt       # Phụ thuộc hệ thống
└── setup.py           # Tệp cài đặt
```

## ⚠️ Vấn đề còn tồn đọng

- **Chữ số viết tay** không được nhận dạng chính xác
- **Hình ảnh mờ** làm giảm độ chính xác của OCR
- **Nền phức tạp** có thể ảnh hưởng đến việc phát hiện bảng
- **Hình ảnh bị biến dạng nghiêm trọng** có thể không xử lý được

## 💡 Một số mẹo để có kết quả tốt nhất

- Đảm bảo **bảng Sudoku hiển thị đầy đủ** trong hình ảnh
- Cố gắng **chụp hình ảnh rõ ràng, đủ sáng** để cải thiện hiệu suất OCR
- Tránh **góc nghiêng hoặc bị biến dạng** để phát hiện bảng tốt hơn
- Sử dụng **Sudoku in hoặc số hóa** để có kết quả tốt nhất
- Bật **cải thiện PicWish** cho hình ảnh chất lượng thấp
- Kiểm tra **hình ảnh Sudoku có ghi chú** nếu câu đố của bạn có số ứng viên

## 🛠️ Packages đi kèm

- Python 3.10+
- OpenCV
- PaddleOCR
- Streamlit
- NumPy
- Pillow
- Picwish

## 📌 Cách sử dụng

1. **Cài đặt cục bộ**
   ```bash
   # Sao chép repository
   git clone https://github.com/ToGiaBaoKDL/Sudoku_OCR.git
   cd Sudoku_OCR

   # Cài đặt các phụ thuộc
   pip install -r requirements.txt

   # Chạy ứng dụng
   streamlit run app/main.py
   ```

2. **Demo trực tuyến**
   - Truy cập [Live Demo](https://sudoku-ocr-tgb.streamlit.app/)
   - Tải lên hoặc dán hình ảnh Sudoku
   - Cấu hình các tùy chọn xử lý ảnh nếu bạn cần
   - Nhận về câu đố đã giải!

## 📝 Giấy phép

Dự án này được cấp phép theo GNU General Public License - xem file LICENSE để biết thêm chi tiết. 
