import socket
import struct
import pickle
import time
import cv2
from config import PC_IP, CAM_PORT, GPS_PORT
from motors import MotorController
from sensors import SensorManager
from vision import VisionDetector

cam_sock = gps_sock = None
try:
    cam_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cam_sock.connect((PC_IP, CAM_PORT))
    gps_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gps_sock.connect((PC_IP, GPS_PORT))
except:
    pass

motors = MotorController()
sensors = SensorManager()
vision = VisionDetector()

try:
    while True:
        ret, frame = vision.get_frame()
        if not ret:
            break

        sensor_data = sensors.get_sensor_data()
        gps_line = sensors.read_gps_line()
        if gps_line and "$GP" in gps_line and gps_sock:
            try:
                gps_sock.sendall((gps_line + sensor_data).encode())
            except:
                gps_sock = None

        if sensors.obstacle_detected():
            motors.kontrol(-50, -50)
            time.sleep(0.5)
            motors.kontrol(60, -60)
            continue

        target_x = vision.detect_target(frame)
        mid = 240
        if target_x is not None:
            motors.kontrol(70, -70) if target_x < mid else motors.kontrol(-70, 70)
        else:
            motors.kontrol(55, 55)

        if cam_sock:
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                data = pickle.dumps(buffer)
                cam_sock.sendall(struct.pack(">L", len(data)) + data)
            except:
                cam_sock = None

except KeyboardInterrupt:
    print("Program durduruldu.")
finally:
    motors.cleanup()
    sensors.cleanup()
    vision.release()
    if cam_sock: cam_sock.close()
    if gps_sock: gps_sock.close()