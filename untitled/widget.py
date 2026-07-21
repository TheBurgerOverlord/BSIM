import sys, json
from PySide6.QtCore import QDir
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QMainWindow, QTreeWidget
from PySide6.QtUiTools import QUiLoader

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
    with open(filePath) as file:
        dicts = []
        for line in file:
            dicts.append(json.loads(line))
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in ContainerTypes:
                Containers.append(type(dictionary["name"], (getContainer(dictionary["parent"]),), dictionary))
                ContainerTypes.append(dictionary["name"])
                dicts.remove(dictionary)

def addContainerToTree(parent, grandparent):
    newNode = QTreeWidgetItem(grandparent,[parent.name + ": " + ", ".join(list(parent.__dict__.keys())[0:-2])])
    for container in Containers:
        if parent.name == container.parent:
            addContainerToTree(container, newNode)

def openFile():
    selectedFile = QFileDialog.getOpenFileUrl()
    if selectedFile[0].toString() != "":
        loadContainers(selectedFile[0].toString().split("//")[1])
        containerTree = mainWindow.findChild(QTreeWidget, "containerTree")
        contTreeRoot = QTreeWidgetItem([ContainerRoot.name + ": " + ", ".join(list(ContainerRoot.__dict__.keys())[0:-2])])
        containerTree.addTopLevelItem(contTreeRoot)
        for container in Containers:
            if container.name == "root":
                continue
            if container.parent == "root":
                addContainerToTree(container, contTreeRoot)


app = QApplication([])

uiLoader = QUiLoader()
mainWindow = uiLoader.load("../interface.ui")
mainWindow.findChild(QAction, "actionOpen_Storage").triggered.connect(openFile)

mainWindow.show()
sys.exit(app.exec())