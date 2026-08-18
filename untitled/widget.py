import sys, json
from zipfile import ZipFile
from PySide6.QtCore import QDir
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QMainWindow, QTreeWidget
from PySide6.QtUiTools import QUiLoader

defaultPath = QDir.homePath()

# CONTAINERS

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

def loadContainers(file):
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

# ITEMS

class Item:
    def __init__(self, parent=None, name=None):
        self.parent = parent
        self.name = name

ItemRoot = type("ItemRoot", (Item,), {"parent":None, "name":"root"})
Items = [ItemRoot]
ItemTypes = ['root']

def getItem(name):
    for item in Items:
        if item.name == name:
            return item
    return None

def loadItems(file):
    dicts = []
    for line in file:
        dicts.append(json.loads(line))
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in ItemTypes:
                Items.append(type(dictionary["name"], (getItem(dictionary["parent"]),), dictionary))
                ItemTypes.append(dictionary["name"])
                dicts.remove(dictionary)

def addItemToTree(parent, grandparent):
    newNode = QTreeWidgetItem(grandparent,[parent.name + ": " + ", ".join(list(parent.__dict__.keys())[0:-2])])
    for item in Items:
        if parent.name == item.parent:
            addItemToTree(item, newNode)

def openDir():
    selectedFile = QFileDialog.getOpenFileUrl()[0].toString().split("//")[1]
    print(selectedFile)
    if selectedFile != "":
        with ZipFile(selectedFile, "r") as zip:
            loadContainers(zip.read("containers.txt").decode())
            containerTree = mainWindow.findChild(QTreeWidget, "containerTree")
            containerTree.clear()
            contTreeRoot = QTreeWidgetItem([ContainerRoot.name + ": " + ", ".join(list(ContainerRoot.__dict__.keys())[0:-2])])
            containerTree.addTopLevelItem(contTreeRoot)
            for container in Containers:
                if container.name == "root":
                    continue
                if container.parent == "root":
                    addContainerToTree(container, contTreeRoot)
            loadItems(zip.read("items.txt").decode())
            itemTree = mainWindow.findChild(QTreeWidget, "itemTree")
            itemTree.clear()
            itemTreeRoot = QTreeWidgetItem([ItemRoot.name + ": " + ", ".join(list(ItemRoot.__dict__.keys())[0:-2])])
            itemTree.addTopLevelItem(itemTreeRoot)
            for item in Items:
                if item.name == "root":
                    continue
                if item.parent == "root":
                    addItemToTree(item, itemTreeRoot)



app = QApplication([])

uiLoader = QUiLoader()
mainWindow = uiLoader.load("../interface.ui")
mainWindow.findChild(QAction, "actionOpen_Storage").triggered.connect(openDir)

mainWindow.show()
sys.exit(app.exec())