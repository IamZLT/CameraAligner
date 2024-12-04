from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
from camera.camera_position import estimate_pose

app = Flask(__name__)

# 全局变量
aligning = False  # 改为对齐状态
capture_device = None
camera_initialized = False
current_camera_index = 0


mtx = np.array([
    [711.77689507, 0, 672.53236606],
    [0, 711.78573804, 313.37884074],
    [0, 0, 1],
])
dist = np.array( [1.26638295e-01, -1.16132908e-01, -2.24690373e-05, -2.25867957e-03, -6.76164003e-02] )


def initialize_camera():
    """初始化摄像头"""
    global capture_device, camera_initialized, current_camera_index
    if not camera_initialized:
        capture_device = cv2.VideoCapture(current_camera_index)
        if not capture_device.isOpened():
            raise Exception(f"Could not open camera {current_camera_index}")
        camera_initialized = True

def release_camera():
    """释放摄像头"""
    global capture_device, camera_initialized
    if camera_initialized and capture_device is not None:
        capture_device.release()
        camera_initialized = False

@app.route('/video-stream')
def video_stream():
    """视频流路由"""
    def generate_frames():
        global capture_device
        while aligning and capture_device:
            success, frame = capture_device.read()
            if not success:
                break
            else:
                # mirrored_frame = cv2.flip(frame, 1)
                mirrored_frame = estimate_pose(frame, mtx, dist)
                resized_frame = cv2.resize(mirrored_frame, (1920, 1080))
                
                _, buffer = cv2.imencode('.jpg', resized_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    if aligning and capture_device:
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({'error': 'Alignment has not started yet.'}), 403

@app.route('/start-align', methods=['POST'])
def start_align():
    """开始对齐"""
    global aligning
    if aligning:
        return jsonify({'success': False, 'error': 'Already aligning'})
    
    initialize_camera()
    aligning = True
    return jsonify({'success': True})

@app.route('/stop-align', methods=['POST'])
def stop_align():
    """停止对齐"""
    global aligning
    if not aligning:
        return jsonify({'success': False, 'error': 'Not currently aligning'})

    aligning = False
    release_camera()
    return jsonify({'success': True})

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')

@app.route('/switch-camera', methods=['POST'])
def switch_camera():
    """切换摄像头"""
    global current_camera_index, capture_device, camera_initialized
    
    try:
        new_camera_index = int(request.form.get('camera_index', 0))
        if camera_initialized and capture_device is not None:
            capture_device.release()
            camera_initialized = False
        
        current_camera_index = new_camera_index
        
        if aligning:
            capture_device = cv2.VideoCapture(current_camera_index)
            if not capture_device.isOpened():
                raise Exception(f"Could not open camera {current_camera_index}")
            camera_initialized = True
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)