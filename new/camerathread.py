import cv2  # OpenCV: 이미지 및 비디오 처리
from PyQt5.QtCore import QThread, pyqtSignal  # PyQt5 스레드 및 신호 처리
from PyQt5.QtGui import QImage  # PyQt5 이미지 처리
from face_register import FaceRegistration  # 얼굴 데이터 처리 클래스

class CameraThread(QThread):
    frame_captured = pyqtSignal(QImage)
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()  # 200장이 완료되면 시그널 발생

    def __init__(self, save_path, user_id):
        super().__init__()
        if save_path is None or user_id is None:
            raise ValueError("save_path와 user_id는 None일 수 없습니다.")
        self.save_path = save_path
        self.user_id = user_id
        self.running = True
        self.face_reg = FaceRegistration()
        self.capture = cv2.VideoCapture(0)
        self.frame_count = 0
        self.max_frames = 200


    def run(self):
        while self.running and self.frame_count < self.max_frames:
            ret, frame = self.capture.read()
            if not ret:
                continue

            faces = self.face_reg.face_extractor(frame)
            if faces:
                self.face_reg.save_faces(faces, self.save_path, self.user_id, self.frame_count)
                self.frame_count += len(faces)
                self.progress_updated.emit(self.frame_count)

            # Convert frame to QImage for UI display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            q_image = QImage(frame_rgb.data, width, height, channel * width, QImage.Format_RGB888)
            self.frame_captured.emit(q_image)

        self.capture.release()
        self.finished.emit()  # 200장 촬영 완료 시 시그널 발생

    def stop(self):
        self.running = False
        self.wait()

