# Ứng dụng Tương tác Không gian AR Thời gian thực bằng MediaPipe & OpenCV

Ứng dụng tương tác thông minh qua webcam sử dụng Python, MediaPipe và OpenCV. Cho phép người dùng sử dụng 4 ngón tay (ngón cái và ngón trỏ của 2 bàn tay) để định hình khung biến đổi động 3D, kết hợp cử chỉ gập ngón tay để thay đổi bộ lọc hiệu ứng thời gian thực.

---

## 🛠️ Cấu trúc dự án
- `main.py`: Mã nguồn chính của ứng dụng.
- `hand_landmarker.task`: Mô hình nhận diện bàn tay MediaPipe.
- `sample.jpg`: Hình ảnh mẫu dùng cho hiệu ứng AR.
- `requirements.txt`: Danh sách các thư viện Python.
- `README.md`: File hướng dẫn cài đặt và sử dụng dự án.

---

## 🌟 Các Tính Năng Chính
- **Định hình 4 góc động (4-Corner Bounding Box):** Co giãn khung linh hoạt bằng 2 bàn tay, hỗ trợ hiệu ứng vặn xoắn phối cảnh 3D.
- **Bộ lọc hiệu ứng đa dạng:** Chuyển đổi qua lại giữa Phủ màu, Trắng đen (Grayscale), Đảo màu (Invert) và Chèn ảnh AR phối cảnh (`sample.jpg`).
- **Tương tác cử chỉ tay (Gesture Control):** Gập ngón áp út và ngón út để chuyển màu / bộ lọc hiệu ứng.
- **Thuật toán thông minh:** Tích hợp bộ lọc làm mượt chuyển động (EMA) chống rung lắc và cơ chế chống dội (Debounce) nhận diện cử chỉ nhạy bén.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Chương Trình

### 1. Yêu cầu hệ thống
- Python 3.8 hoặc mới hơn.
- Webcam máy tính hoạt động ổn định.

### 2. Cài đặt các thư viện cần thiết
Mở Terminal / Command Prompt tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

---

## 🎮 Hướng Dẫn Sử Dụng & Thao Tác
- **Tạo & co giãn khung AR:** Đưa 2 bàn tay lên camera, sử dụng 4 ngón tay (ngón cái và ngón trỏ của 2 bàn tay) để tạo thành 4 góc của khung. Di chuyển tay rộng/hẹp để co giãn khung.
- **Hiệu ứng vặn xoắn:** Đan chéo 2 bàn tay để tạo hiệu ứng vặn xoắn 3D (hình chiếc nơ / bowtie).
- **Đổi hiệu ứng / màu sắc:** Gập đồng thời ngón áp út và ngón út của bàn tay chính để chuyển đổi qua lại giữa các chế độ màu và bộ lọc.
- **Thoát ứng dụng:** Nhấn phím **`q`** trên bàn phím.