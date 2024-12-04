import numpy as np
import cv2
import cv2.aruco as aruco
import math

from enum import Enum


class ArucoDictionary(Enum):
    Dict_4X4_50 = aruco.DICT_4X4_50
    Dict_4X4_100 = aruco.DICT_4X4_100
    Dict_4X4_250 = aruco.DICT_4X4_250
    Dict_4X4_1000 = aruco.DICT_4X4_1000
    Dict_5X5_50 = aruco.DICT_5X5_50
    Dict_5X5_100 = aruco.DICT_5X5_100
    Dict_5X5_250 = aruco.DICT_5X5_250
    Dict_5X5_1000 = aruco.DICT_5X5_1000
    Dict_6X6_50 = aruco.DICT_6X6_50
    Dict_6X6_100 = aruco.DICT_6X6_100
    Dict_6X6_250 = aruco.DICT_6X6_250
    Dict_6X6_1000 = aruco.DICT_6X6_1000
    Dict_7X7_50 = aruco.DICT_7X7_50
    Dict_7X7_100 = aruco.DICT_7X7_100
    Dict_7X7_250 = aruco.DICT_7X7_250
    Dict_7X7_1000 = aruco.DICT_7X7_1000
    Dict_APRILTAG_16h5 = aruco.DICT_APRILTAG_16h5
    Dict_APRILTAG_25h9 = aruco.DICT_APRILTAG_25h9
    Dict_APRILTAG_36h10 = aruco.DICT_APRILTAG_36h10
    Dict_APRILTAG_36h11 = aruco.DICT_APRILTAG_36h11
    Dict_ArUco_ORIGINAL = aruco.DICT_ARUCO_ORIGINAL

# cap = cv2.VideoCapture(0)

# # 设置视频流的分辨率为 1280x720
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

DICTIONARY = ArucoDictionary.Dict_4X4_50
markerIds = 0

dictionary = aruco.getPredefinedDictionary(DICTIONARY.value)

def estimate_pose(frame, mtx, dist):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    parameters = aruco.DetectorParameters()

    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    # 检测 ArUco 标记
    marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(gray)

    # 输出结果
    # print("Detected marker IDs:", marker_ids)
    # print("Marker corners:", marker_corners)
    # print("Rejected candidates:", rejected_candidates)

    # 检测图像中的ArUco标记
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 如果检测到ArUco标记
    if marker_ids is not None and len(marker_ids) > 0:
        for i in range(len(marker_ids)):  # 遍历每个检测到的ArUco标记
            # 估计ArUco标记的姿态（旋转向量和平移向量）
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(marker_corners[i], 0.10, mtx, dist)

            R, _ = cv2.Rodrigues(rvec)  # 将旋转向量（rvec）转换为旋转矩阵（R）3*3
            R_inv = np.transpose(R)  # 旋转矩阵是正交矩阵，所以它的逆矩阵等于它的转置 R_inv 表示从相机坐标系到标记坐标系的旋转。
            if tvec.shape != (3, 1):
                tvec_re = tvec.reshape(3, 1)
                #print('-------tvec_re------')
                #print(tvec_re)

            tvec_inv = -R_inv @ tvec_re
            tvec_inv1 = np.transpose(tvec_inv)
            pos = tvec_inv1[0]
            print(pos)
            distance = math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
            rad = pos[0]/pos[2]
            angle_in_radians = math.atan(rad)
            angle_in_degrees = math.degrees(angle_in_radians)


            # 绘制ArUco标记的坐标轴
            cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, 0.05)

            tvec_inv_str = " ".join([f"{num:.2f}m" for num in tvec_inv1.flatten()])
            cv2.putText(frame, "tvec_inv: " + tvec_inv_str, (0, 80), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, 'distance:' + str(round(distance, 4)) + str('m'), (0, 110), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, "degree: " + str(angle_in_degrees), (0, 150), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # 获取ArUco标记相对于相机坐标系的位置
            # pos_str_cam = f"X: {tvec_inv1[0][0][0]:.2f}m, Y: {tvec_inv1[0][0][1]:.2f}m, Z: {tvec[0][0][2]:.2f}m"

            # 在图像上标注ArUco标记的相对于相机坐标系的位置信息
            # cv2.putText(frame, pos_str_cam, (int(corners[i][0][0][0]), int(corners[i][0][0][1]) - 10),
            #             font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)



        # 在图像上绘制检测到的ArUco标记
        aruco.drawDetectedMarkers(frame, marker_corners)

    # 如果没有检测到ArUco标记，则在图像上显示"No Ids"
    else:
        cv2.putText(frame, "No Ids", (0, 64), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    return frame  # 返回处理后的图像


# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#     mtx = np.array([
#         [711.77689507, 0, 672.53236606],
#         [0, 711.78573804, 313.37884074],
#         [0, 0, 1],
#     ])
#     dist = np.array( [1.26638295e-01, -1.16132908e-01, -2.24690373e-05, -2.25867957e-03, -6.76164003e-02] )
#     # 调用estimate_pose函数对当前帧进行姿态估计和标记检测
#     frame = estimate_pose(frame, mtx, dist)
#     new_width = 1280
#     new_height = 720
#     frame = cv2.resize(frame, (new_width, new_height))
#     cv2.imshow('frame', frame)

#     # 等待按键输入，如果按下键盘上的'q'键则退出循环
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # 释放VideoCapture对象
# cap.release()
# cv2.destroyAllWindows()
