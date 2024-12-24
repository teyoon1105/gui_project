import sys
import os
import csv
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QProgressBar
from main_window import Ui_MainWindow
from face_register import FaceRegistration
from face_recognize import FaceRecognition
from camerathread import CameraThread


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.face_reg = FaceRegistration()
        self.face_rec = FaceRecognition(use_tts=True)  # TTS 활성화
        self.current_user_info = None
        self.camera_thread = None

        # 버튼 연결
        self.ui.btnSettings.clicked.connect(self.open_registration_window)
        self.ui.btnNext4.clicked.connect(self.save_user_info)
        self.ui.btnNext5.clicked.connect(self.start_face_capture)
        self.ui.btnHome5.clicked.connect(self.stop_face_capture)
        self.ui.btnStart.clicked.connect(self.start_face_recognition)
        self.ui.btnNext1.clicked.connect(self.move_to_window2)  # Window1 -> Window2
        self.ui.btnHome1.clicked.connect(self.return_to_home)  # Window1 -> Home

        # Progress bar 설정 (window5)
        self.ui.progressBar = QProgressBar(self.ui.window5)
        self.ui.progressBar.setGeometry(50, 50, 400, 30)
        self.ui.progressBar.setMaximum(200)

    # ---------------------------------------
    # Registration 기능 (Window 4, 5)
    # ---------------------------------------
    def open_registration_window(self):
        """사용자 등록 화면으로 이동"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.window4)

    def save_user_info(self):
        """사용자 정보를 저장 (window4)"""
        user_info = {
            "아이디": self.face_reg.generate_folder("train")[0],
            "이름": self.ui.editName.text(),
            "생년월일": self.ui.editBirth.text(),
            "성별": self.ui.comboGender.currentText(),
            "연락처": self.ui.editPhone.text(),
            "주소": self.ui.editAddress.text(),
            "키": self.ui.editHeight.text(),
            "몸무게": self.ui.editWeight.text(),
        }

        if not all(user_info.values()):
            QMessageBox.warning(self, "Error", "모든 정보를 입력하세요.")
            return

        # 사용자 정보 CSV 저장
        self.face_reg.save_csv(user_info)
        self.current_user_info = user_info
        QMessageBox.information(self, "Success", "사용자 정보가 저장되었습니다.")
        self.ui.stackedWidget.setCurrentWidget(self.ui.window5)

    def start_face_capture(self):
        """얼굴 데이터 캡처 시작 (window5)"""
        if not self.current_user_info:
            QMessageBox.warning(self, "Error", "사용자 정보를 저장해야 합니다.")
            return

        user_id = self.current_user_info.get("아이디")
        if not user_id:
            QMessageBox.warning(self, "Error", "사용자 ID가 없습니다.")
            return

        save_path = os.path.join("train", user_id)
        os.makedirs(save_path, exist_ok=True)

        self.camera_thread = CameraThread(save_path, user_id)
        self.camera_thread.frame_captured.connect(self.display_training_frame)
        self.camera_thread.progress_updated.connect(self.update_progress_bar)
        self.camera_thread.finished.connect(self.on_face_capture_complete)
        self.camera_thread.start()

    def display_training_frame(self, q_image):
        """캡처된 프레임을 UI에 표시"""
        self.ui.cameraTrainingFrame.setPixmap(QPixmap.fromImage(q_image))

    def update_progress_bar(self, value):
        """Progress bar 업데이트"""
        self.ui.progressBar.setValue(value)

    def on_face_capture_complete(self):
        """얼굴 데이터 캡처 완료 시 처리"""
        QMessageBox.information(self, "Success", "얼굴 데이터 수집이 완료되었습니다.")
        train_path = os.path.join("train", self.current_user_info["아이디"])
        self.face_reg.train_model(train_path)
        self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)

    def stop_face_capture(self):
        """홈 버튼 클릭 시 캡처 중단"""
        if self.camera_thread:
            self.camera_thread.stop()
            QMessageBox.information(self, "Info", "캡처가 중단되었습니다.")
            self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)

    # ---------------------------------------
    # Recognition 기능 (Window 1)
    # ---------------------------------------
    def start_face_recognition(self):
        """Start 버튼 클릭 시 얼굴 인식 실행"""
        try:
            # CSV에서 사용자 데이터 읽기
            if not os.path.exists("user_info.csv"):
                QMessageBox.warning(self, "Error", "등록된 사용자 정보가 없습니다.")
                return

            with open("user_info.csv", "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                user_data = list(reader)

            if not user_data:
                QMessageBox.warning(self, "Error", "등록된 사용자 정보가 없습니다.")
                return

            # 모델 파일 경로 확인
            model_path = os.path.join("train", "trained_model.yml")
            if not os.path.exists(model_path):
                QMessageBox.warning(self, "Error", "모델 파일이 없습니다. 먼저 학습을 완료하세요.")
                return

            # 모델 로드
            self.face_rec.load_model(model_path)
            QMessageBox.information(self, "Success", "모델이 성공적으로 로드되었습니다.")
            
            # 얼굴 인식 시작
            cap = cv2.VideoCapture(0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue

                # 얼굴 인식
                result, annotated_frame = self.face_rec.recognize_faces(frame, user_data)
                
                # 결과 화면에 표시
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                q_image = QImage(frame_rgb.data, width, height, channel * width, QImage.Format_RGB888)
                self.ui.camera1Frame.setPixmap(QPixmap.fromImage(q_image))

                if cv2.waitKey(1) & 0xFF == 27:  # ESC 키로 종료
                    break

            cap.release()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"얼굴 인식 중 오류가 발생했습니다:\n{e}")

    def on_face_recognition_complete(self):
        """얼굴 인식 완료 후 처리"""
        QMessageBox.information(self, "Success", "얼굴이 인식되었습니다.")
        self.ui.stackedWidget.setCurrentWidget(self.ui.window2)

    def move_to_window2(self):
        """Window1 -> Window2로 이동"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.window2)

    def return_to_home(self):
        """Window1 -> Home으로 이동"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    sys.exit(app.exec_())
