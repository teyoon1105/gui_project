from PyQt5 import QtCore, QtWidgets

class ListDisplayWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("window2")
        self.resize(1200, 700)

        self.camera_frame = QtWidgets.QLabel("Camera 2 Frame", self)
        self.camera_frame.setGeometry(QtCore.QRect(20, 40, 880, 640))
        self.camera_frame.setAlignment(QtCore.Qt.AlignCenter)

        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setGeometry(QtCore.QRect(920, 40, 250, 521))

        self.btn_complete = QtWidgets.QPushButton("Complete", self)
        self.btn_complete.setGeometry(QtCore.QRect(920, 580, 250, 100))
