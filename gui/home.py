from PySide6.QtWidgets import QWidget


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("HomePage")

    def initUI(self):
        ...
