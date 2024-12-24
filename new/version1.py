import sys
import os
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QProgressBar
from main_window import Ui_MainWindow
from face_register import FaceRegistration
from camerathread import CameraThread  # CameraThread 파일에서 가져옴


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.face_reg = FaceRegistration()
        self.current_user_info = None
        self.camera_thread = None

        # Connect buttons
        self.ui.btnSettings.clicked.connect(self.open_registration_window)
        self.ui.btnNext4.clicked.connect(self.save_user_info)
        self.ui.btnNext5.clicked.connect(self.start_face_capture)

        # Progress bar setup
        self.ui.progressBar = QProgressBar(self.ui.window5)
        self.ui.progressBar.setGeometry(50, 50, 400, 30)
        self.ui.progressBar.setMaximum(200)

    def open_registration_window(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.window4)

    def save_user_info(self):
        """window4에서 사용자 정보를 저장"""
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
        self.face_reg.save_csv(user_info)  # FaceRegistration 클래스의 save_csv 호출
        self.current_user_info = user_info  # 정보 저장
        QMessageBox.information(self, "Success", "정보가 저장되었습니다.")
        self.ui.stackedWidget.setCurrentWidget(self.ui.window5)  # window5로 이동

    def start_face_capture(self):
        if not self.current_user_info:
            QMessageBox.warning(self, "Error", "사용자 정보를 저장해야 합니다.")
            return

        user_id = self.current_user_info["아이디"]
        save_path = os.path.join("train", user_id)
        os.makedirs(save_path, exist_ok=True)

        self.camera_thread = CameraThread(save_path, user_id)
        self.camera_thread.frame_captured.connect(self.display_training_frame)
        self.camera_thread.progress_updated.connect(self.update_progress_bar)
        self.camera_thread.finished.connect(self.on_face_capture_complete)  # 종료 시 이벤트 연결
        self.camera_thread.start()

    def display_training_frame(self, q_image):
        self.ui.cameraTrainingFrame.setPixmap(QPixmap.fromImage(q_image))

    def update_progress_bar(self, value):
        self.ui.progressBar.setValue(value)

    def on_face_capture_complete(self):
        QMessageBox.information(self, "Success", "얼굴 데이터 수집이 완료되었습니다.")
        train_path = os.path.join("train", self.current_user_info["아이디"])
        self.face_reg.train_model(train_path)
        self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    sys.exit(app.exec_())
