import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file
        ui_file = QFile("main.ui")  # UI 파일 경로
        if not ui_file.open(QFile.ReadOnly):
            print(f"Cannot open {ui_file.fileName()}: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if not self.ui:
            print(loader.errorString())
            sys.exit(-1)

        # Connect buttons to functions
        self.ui.btnStart.clicked.connect(lambda: self.change_page("window1"))
        self.ui.btnSettings.clicked.connect(lambda: self.change_page("window4"))
        self.ui.btnHome1.clicked.connect(lambda: self.change_page("homeWindow"))
        self.ui.btnNext1.clicked.connect(lambda: self.change_page("window2"))
        self.ui.btnComplete.clicked.connect(lambda: self.change_page("window3"))
        self.ui.btnHome3.clicked.connect(lambda: self.change_page("homeWindow"))
        self.ui.btnHome4.clicked.connect(lambda: self.change_page("homeWindow"))
        self.ui.btnNext4.clicked.connect(lambda: self.change_page("window5"))
        self.ui.btnHome5.clicked.connect(lambda: self.change_page("homeWindow"))
        self.ui.btnNext5.clicked.connect(lambda: self.change_page("window6"))
        self.ui.btnHome6.clicked.connect(lambda: self.change_page("homeWindow"))

        # Set the initial page
        self.ui.stackedWidget.setCurrentWidget(self.ui.homeWindow)

        # Show the UI
        self.ui.show()

    def change_page(self, page_name):
        """Change the current page in QStackedWidget."""
        widget = getattr(self.ui, page_name, None)
        if widget:
            self.ui.stackedWidget.setCurrentWidget(widget)
        else:
            print(f"Page {page_name} not found!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
