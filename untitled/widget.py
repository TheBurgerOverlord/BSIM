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


class Container:
    def __init__(self, parent, children, name, contid, attributes={}):
        self.parent = parent
        self.children = children
        self.name = name
        self.contid = contid
        if self.parent is not None:
            self.attributes = dict(parent.attributes)
            self.attributes.update(attributes)
        else:
            self.attributes = attributes


class Item:
    def __init__(self, parent, children, name, itemid, attributes={}):
        self.parent = parent
        self.children = children
        self.name = name
        self.itemid = itemid
        if self.parent is not None:
            self.attributes = dict(parent.attributes)
            self.attributes.update(attributes)
        else:
            self.attributes = attributes


ContainerObject = Container(None, [], "ContainerObject", "root", {"location": "/"})
ItemObject = Container(None, [], "ItemObject", "root", {"location": "/"})

def makedirforchildren(path):


def loadcontainers():
    for name in os.listdir(currentPath):
        path = os.path.join(currentPath, name)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (path, e))
    global ContainerObject

    containers = QFileSystemModel()
    containers.setRootPath(currentPath + "/ContainerObject")


if __name__ == "__main__":
    app = QApplication([])
    window = uic.loadUi("../interface.ui")
    window.show()
    sys.exit(app.exec())
