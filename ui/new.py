import sys
from PyQt5 import QtWidgets
from main_window import Ui_MainWindow
import FaceRegistration
import FaceRecognition


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 등록 및 인식 클래스 초기화
        self.face_reg = FaceRegistration()
        self.face_rec = FaceRecognition()

        # 버튼 이벤트 연결
        self.ui.btnSettings.clicked.connect(self.open_registration_window)
        self.ui.btnStart.clicked.connect(self.start_recognition)
        self.ui.btnNext4.clicked.connect(self.save_user_info)
        self.ui.btnNext5.clicked.connect(self.capture_faces)

    def open_registration_window(self):
        """Settings 버튼 클릭 시 등록 화면으로 이동"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.window4)

    def save_user_info(self):
        """사용자 정보 저장"""
        user_info = {
            "아이디": self.ui.editName.text(),
            "이름": self.ui.editName.text(),
            "생년월일": self.ui.editAge.text(),
            "성별": self.ui.comboGender.currentText(),
            "연락처": self.ui.editPhone.text(),
            "주소": "",
            "키": 0,
            "몸무게": 0,
            "운동량": ""
        }

        if not all(user_info.values()):
            QtWidgets.QMessageBox.warning(self, "Error", "모든 정보를 입력하세요.")
            return

        self.current_user_info = user_info  # 저장
        QtWidgets.QMessageBox.information(self, "Success", "정보가 저장되었습니다.")
        self.ui.stackedWidget.setCurrentWidget(self.ui.window5)

    def capture_faces(self):
        """얼굴 데이터 캡처 및 학습"""
        self.face_reg.save_csv(self.current_user_info)
        self.face_reg.capture_faces(self.current_user_info)

        QtWidgets.QMessageBox.information(self, "Success", "얼굴 캡처 및 모델 학습이 완료되었습니다.")
        self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)

    def start_recognition(self):
        """얼굴 인식 시작"""
        try:
            with open("user_info.csv", "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                user_data = next(reader)
                user_name = user_data["이름"]
                train_path = f"train/{user_data['아이디']}"

                # 얼굴 인식 실행
                self.face_rec.recognize_faces(user_name, train_path)

                QtWidgets.QMessageBox.information(self, "Success", f"{user_name}님 환영합니다!")
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(self, "Error", "등록된 사용자가 없습니다.")
        except StopIteration:
            QtWidgets.QMessageBox.warning(self, "Error", "등록된 사용자가 없습니다.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    sys.exit(app.exec_())
