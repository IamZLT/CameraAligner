import cv2

# 打开摄像头，使用索引 0（可以尝试更改为 1 或其他索引）
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("Cannot open camera")
else:
    print("Press 'q' to exit.")

    while True:
        # 从摄像头读取帧
        ret, frame = cap.read()

        # 如果读取失败，跳出循环
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # 对帧进行水平镜像翻转（1 表示水平翻转，0 表示垂直翻转）
        mirrored_frame = cv2.flip(frame, 1)

        # 显示捕获的画面
        cv2.imshow('Live Camera Feed (Mirrored)', mirrored_frame)

        # 检测键盘输入，如果按下 'q' 键，退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

# 释放摄像头资源
cap.release()

# 关闭所有 OpenCV 窗口
cv2.destroyAllWindows()