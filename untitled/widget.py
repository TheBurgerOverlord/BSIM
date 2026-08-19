import sys, json
from zipfile import ZipFile
from PySide6.QtCore import QDir
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QMainWindow, QTreeWidget, QMenu, QMessageBox, \
    QDialogButtonBox, QLineEdit, QPlainTextEdit
from PySide6.QtUiTools import QUiLoader

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

def addContainer(name, parent, properties):
    if getContainer(name):
        raise Exception(f"Container with name {name} already exists")
    parentNameDict = {"name":name, "parent":parent}
    Containers.append(type(name, (getContainer(parent),), parentNameDict|properties))
    ContainerTypes.append(name)

def loadContainers(file):
    global ContainerRoot, Containers, ContainerTypes
    Containers = [ContainerRoot]
    ContainerTypes = ['root']
    dicts = []
    for line in file.splitlines():
        dicts.append(json.loads(line))
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in ContainerTypes:
                addContainer(dictionary["name"], dictionary["parent"], dictionary)
                dicts.remove(dictionary)

def addContainerToTree(parent, grandparent):
    newNode = QTreeWidgetItem(grandparent,[parent.name + ": " + ", ".join(list(parent.__dict__.keys())[2:-2])])
    for container in Containers:
        if parent.name == container.parent:
            addContainerToTree(container, newNode)

def loadContainersToTree(tree):
    tree.clear()
    contTreeRoot = QTreeWidgetItem([ContainerRoot.name + ": " + ", ".join(list(ContainerRoot.__dict__.keys())[0:-2])])
    tree.addTopLevelItem(contTreeRoot)
    for container in Containers:
        if container.name == "root":
            continue
        if container.parent == "root":
            addContainerToTree(container, contTreeRoot)

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

def addItem(name, parent, properties):
    if getItem(name):
        raise Exception(f"Item with name {name} already exists")
    parentNameDict = {"name":name, "parent":parent}
    Items.append(type(name, (getItem(parent),), parentNameDict|properties))
    ItemTypes.append(name)

def loadItems(file):
    global ItemRoot, Items, ItemTypes
    Items = [ItemRoot]
    ItemTypes = ['root']
    dicts = []
    for line in file.splitlines():
        dicts.append(json.loads(line))
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in ItemTypes:
                addItem(dictionary["name"], dictionary["parent"], dictionary)
                dicts.remove(dictionary)

def addItemToTree(parent, grandparent):
    newNode = QTreeWidgetItem(grandparent,[parent.name + ": " + ", ".join(list(parent.__dict__.keys())[2:-2])])
    for item in Items:
        if parent.name == item.parent:
            addItemToTree(item, newNode)

def loadItemsToTree(tree):
    tree.clear()
    itemTreeRoot = QTreeWidgetItem([ItemRoot.name + ": " + ", ".join(list(ItemRoot.__dict__.keys())[0:-2])])
    tree.addTopLevelItem(itemTreeRoot)
    for item in Items:
        if item.name == "root":
            continue
        if item.parent == "root":
            addItemToTree(item, itemTreeRoot)

# other stuff

def openDir():
    selectedFile = QFileDialog.getOpenFileUrl()[0].toString().split("//")[1]
    if selectedFile != "":
        try:
            ZipFile(selectedFile, "r")
        except Exception:
            msg = QMessageBox()
            msg.setText("Invalid file")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.exec()
        with ZipFile(selectedFile, "r") as zip:
            loadContainers(zip.read("containers.txt").decode())
            loadContainersToTree(containerTree)
            loadItems(zip.read("items.txt").decode())
            loadItemsToTree(itemTree)
    global currentFile
    currentFile = selectedFile
    mainWindow.setWindowTitle(f"BSIM - {currentFile}")

def newContainerOpenGUI():
    loadContainersToTree(selectContainer)
    newContWindow.show()

def newContainerProcess():
    properties = {}
    for line in containerPropertyInput.toPlainText().splitlines():
        properties[line] = 0
    if not properties:
        msg = QMessageBox()
        msg.setText("Container must have properties")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    name = containerNameInput.text()
    if not name:
        msg = QMessageBox()
        msg.setText("Container must have a name")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    parent = selectContainer.selectedItems()[0].text(0).split(":")[0]
    if not parent:
        msg = QMessageBox()
        msg.setText("Container needs a parent")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    addContainer(name, parent, properties)
    loadContainersToTree(containerTree)

def newItemOpenGUI():
    loadItemsToTree(selectItem)
    newItemWindow.show()

def newItemProcess():
    properties = {}
    for line in itemPropertyInput.toPlainText().splitlines():
        properties[line] = 0
    if not properties:
        msg = QMessageBox()
        msg.setText("Item must have properties")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    name = itemNameInput.text()
    if not name:
        msg = QMessageBox()
        msg.setText("Item must have a name")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    parent = selectItem.selectedItems()[0].text(0).split(":")[0]
    if not parent:
        msg = QMessageBox()
        msg.setText("Item needs a parent")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    addItem(name, parent, properties)
    loadItemsToTree(itemTree)

currentFile = None

app = QApplication([])
uiLoader = QUiLoader()

mainWindow = uiLoader.load("../interface.ui")
newContWindow = uiLoader.load("../newCont.ui")
newItemWindow = uiLoader.load("../newItem.ui")

containerTree = mainWindow.findChild(QTreeWidget, "containerTree")
itemTree = mainWindow.findChild(QTreeWidget, "itemTree")

mainWindow.findChild(QAction, "actionOpen_Storage").triggered.connect(openDir)
mainWindow.findChild(QAction, "actionNew_Container").triggered.connect(newContainerOpenGUI)
mainWindow.findChild(QAction, "actionNew_Item").triggered.connect(newItemOpenGUI)

selectContainer = newContWindow.findChild(QTreeWidget, "contSelector")
containerNameInput = newContWindow.findChild(QLineEdit, "nameInput")
containerPropertyInput = newContWindow.findChild(QPlainTextEdit, "propertyInput")

selectItem = newItemWindow.findChild(QTreeWidget, "itemSelector")
itemNameInput = newItemWindow.findChild(QLineEdit, "nameInput")
itemPropertyInput = newItemWindow.findChild(QPlainTextEdit, "propertyInput")

newContWindow.findChild(QDialogButtonBox, "buttonBox").accepted.connect(newContainerProcess)
newItemWindow.findChild(QDialogButtonBox, "buttonBox").accepted.connect(newItemProcess)

mainWindow.show()
sys.exit(app.exec())