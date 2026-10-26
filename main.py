import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import urllib.request

# 1. Tự động tải file model nhận diện bàn tay nếu chưa có
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Đang tải model MediaPipe HandLandmarker...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Tải model thành công!")

# 2. Khởi tạo HandLandmarker API
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detector = vision.HandLandmarker.create_from_options(options)

# 3. Khởi tạo Webcam
cap = cv2.VideoCapture(0)

# Đặt tên cửa sổ và cấu hình cho phép phóng to/thu nhỏ linh hoạt
window_name = 'Smooth AR Frame - Assignment'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# DANH SÁCH TRẠNG THÁI HIỆU ỨNG (Màu sắc, Trắng đen, Đảo màu, Ảnh mẫu)
STATES = ["COLOR_BLUE", "COLOR_GREEN", "GRAYSCALE", "INVERT", "IMAGE_SAMPLE"]
state_index = 0
is_gesture_prev = False  # Biến chống dội cho cử chỉ gập ngón

# Tải file ảnh sample.jpg và chuẩn hóa hướng xoay
sample_img_path = 'sample.jpg'
if os.path.exists(sample_img_path):
    sample_img = cv2.imread(sample_img_path)
    sample_img = cv2.rotate(sample_img, cv2.ROTATE_90_CLOCKWISE)
    img_h, img_w, _ = sample_img.shape
    print("-> Đã tải và chuẩn hóa hướng ảnh 'sample.jpg' thành công!")
else:
    sample_img = None
    print("-> Không tìm thấy 'sample.jpg', trạng thái IMAGE_SAMPLE sẽ bỏ qua.")

# Biến nhớ lưu vết tọa độ khung để làm mượt
prev_pts = np.array([[150, 150], [350, 150], [350, 350], [150, 350]], dtype=np.float32)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Không thể mở camera.")
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    detection_result = detector.detect(mp_image)

    is_hands_detected = False
    current_pts = []

    # Yêu cầu bắt buộc: Nhận diện đủ 2 bàn tay (4 ngón: cái + trỏ của 2 tay)
    if detection_result.hand_landmarks and len(detection_result.hand_landmarks) >= 2:
        is_hands_detected = True
        
        hands = sorted(detection_result.hand_landmarks, key=lambda l: l[0].x)
        h1 = hands[0] # Tay trái
        h2 = hands[1] # Tay phải
        
        t1 = [int(h1[4].x * w), int(h1[4].y * h)]  # Ngón cái tay trái
        i1 = [int(h1[8].x * w), int(h1[8].y * h)]  # Ngón trỏ tay trái
        i2 = [int(h2[8].x * w), int(h2[8].y * h)]  # Ngón trỏ tay phải
        t2 = [int(h2[4].x * w), int(h2[4].y * h)]  # Ngón cái tay phải
        
        current_pts = [t1, i1, i2, t2]

        # Nhận diện cử chỉ gập ngón áp út (16) và ngón út (20) để chuyển đổi trạng thái
        primary_hand = hands[0]
        ring_folded = primary_hand[16].y > primary_hand[14].y
        pinky_folded = primary_hand[20].y > primary_hand[18].y
        is_gesture_active = ring_folded and pinky_folded
        
        if is_gesture_active and not is_gesture_prev:
            state_index = (state_index + 1) % len(STATES)
            print(f"-> Chuyển trạng thái hiệu ứng: {STATES[state_index]}")
        is_gesture_prev = is_gesture_active

    # XỬ LÝ ĐỒ HỌA: Áp dụng hiệu ứng mượt mà khi đủ 2 tay, không vẽ viền hay đầu mút
    if is_hands_detected and len(current_pts) == 4:
        target_pts = np.array(current_pts, dtype=np.float32)
        
        # THUẬT TOÁN LÀM MƯỢT (Exponential Smoothing) giúp triệt tiêu rung lắc
        alpha_smooth = 0.35  
        prev_pts = alpha_smooth * target_pts + (1 - alpha_smooth) * prev_pts
        
        pts_array = prev_pts.astype(np.int32)
        current_state = STATES[state_index]

        # Tạo mặt nạ (Mask) cho đa giác 4 góc ngón tay
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [pts_array], 255)
        mask_inv = cv2.bitwise_not(mask)
        
        # Tách phần nền bên ngoài khung
        bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        fg = np.zeros_like(frame)

        # Xử lý hiệu ứng độc lập bên trong vùng đa giác
        if current_state.startswith("COLOR_"):
            colors_map = {
                "COLOR_BLUE": (255, 120, 120),
                "COLOR_GREEN": (120, 255, 120)
            }
            fill_color = colors_map.get(current_state, (120, 120, 255))
            colored_layer = frame.copy()
            colored_layer[:] = fill_color
            blended = cv2.addWeighted(colored_layer, 0.4, frame, 0.6, 0)
            fg = cv2.bitwise_and(blended, blended, mask=mask)

        elif current_state == "GRAYSCALE":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            fg = cv2.bitwise_and(gray_bgr, gray_bgr, mask=mask)

        elif current_state == "INVERT":
            inverted = cv2.bitwise_not(frame)
            fg = cv2.bitwise_and(inverted, inverted, mask=mask)

        elif current_state == "IMAGE_SAMPLE" and sample_img is not None:
            try:
                src_pts = np.float32([[0, 0], [img_w, 0], [img_w, img_h], [0, img_h]])
                dst_pts = prev_pts.astype(np.float32)
                matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped_img = cv2.warpPerspective(sample_img, matrix, (w, h))
                fg = cv2.bitwise_and(warped_img, warped_img, mask=mask)
            except Exception:
                fg = cv2.bitwise_and(frame, frame, mask=mask)

        # Ghép nền và hiệu ứng lại với nhau
        frame = cv2.add(bg, fg)

    # Hiển thị thông tin giao diện tối giản
    cv2.putText(frame, f"Mode: {STATES[state_index]}", (30, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to exit", (30, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow(window_name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()