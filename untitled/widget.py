import sys, json
from PyQt6.QtCore import QDir
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6 import uic

defaultPath = QDir.homePath()

class Container:
    def __init__(self, parent=None, name=None):
        self.parent = parent
        self.name = name

ContainerRoot = type("ContainerRoot", (Container,), {"parent":None, "name":"root"})
Containers = [ContainerRoot]
ContainerTypes = ['root']

def getContainer(name):
    for container in Containers:
        if container.name == name:
            return container
    return None

def loadContainers(filePath):
    print("Loading containers from file...")
    with open(filePath) as file:
        dicts = []
        for line in file:
            dicts.append(json.loads(line))
    print("Building container tree..")
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in ContainerTypes:
                Containers.append(type(dictionary["name"], (getContainer(dictionary["parent"]),), dictionary))
                ContainerTypes.append(dictionary["name"])
                dicts.remove(dictionary)

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BSIM - v0.0.1 (alpha)")
    def openFile(self):
        selectedFile = QFileDialog.getOpenFileUrl()
        loadContainers(selectedFile[0].toString().split("//")[1])

if __name__ == "__main__":
    app = QApplication([])
    window = uic.loadUi("../interface.ui")
    window.show()
    sys.exit(app.exec())
