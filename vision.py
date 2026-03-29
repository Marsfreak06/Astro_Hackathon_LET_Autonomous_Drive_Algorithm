import cv2
from ultralytics import YOLO
from config import CONF_LEVEL, IMG_SIZE

class VisionDetector:
    def __init__(self):
        self.model = YOLO('best.pt')
        self.model.to('cpu')
        self.det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50))
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    def get_frame(self):
        ret, frame = self.cap.read()
        return ret, frame

    def detect_target(self, frame):
        target_x = None
        corners, ids, _ = self.det.detectMarkers(frame)
        if ids is not None and len(ids) > 0:
            c = corners[0][0]
            target_x = int((c[:, 0].max() + c[:, 0].min()) / 2)
        else:
            res = self.model.predict(frame, conf=CONF_LEVEL, imgsz=IMG_SIZE, verbose=False, stream=True)
            for r in res:
                if len(r.boxes) > 0:
                    b = r.boxes[0].xyxy[0].cpu().numpy()
                    target_x = int((b[0] + b[2]) / 2)
                break
        return target_x

    def release(self):
        self.cap.release()

if __name__ == "__main__":
    print("VisionDetector test ediliyor...")
    vision = VisionDetector()
    ret, frame = vision.get_frame()
    if ret:
        tx = vision.detect_target(frame)
        print("Hedef X koordinatı:", tx)
    vision.release()