import os
import shutil
import sys
from PyQt6.QtCore import QDir
from PySide6.QtWidgets import QApplication, QWidget, QFileSystemModel
from PyQt6 import uic

#defaultPath = QDir.homePath()
defaultPath = "/run/media/system/Data/BSIM/testingStorage"
currentPath = defaultPath

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

if __name__ == "__main__":
    app = QApplication([])
    window = uic.loadUi("../interface.ui")
    window.show()
    sys.exit(app.exec())
