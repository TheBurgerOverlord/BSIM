# IMPORTS

import json
import sys
from zipfile import ZipFile

from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QTreeWidget, QMessageBox, \
    QDialogButtonBox, QLineEdit, QPlainTextEdit, QListView, QListWidget


# CONTAINERS

class Container:
    def __init__(self, parent=None, name=None):
        self.parent = parent
        self.name = name

ContainerRoot = type("ContainerRoot", (Container,), {"parent":None,"name":"root","displayName":"Container","storageID":"root"})
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

ItemRoot = type("ItemRoot", (Item,), {"parent":None,"name":"root","displayName":"Item","storageID":"root"})
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

# STORAGE

StorageRoot = type("StorageRoot", (ContainerRoot,), {"parent":None, "name":"root","displayName":"StorageRoot","storageID":0,"isContainer":True})
Storage = [StorageRoot]
StorageIDs = [0]

def getElementByID(id):
    for element in Storage:
        if element.storageID == id:
            return element
    return None

def addContainerToStorage(containerName, storageParentID, displayName, properties, id=None):
    if id:
        storageID = id
    else:
        storageID = max(StorageIDs) + 1
    parentNameDict = {"name":containerName, "parent":int(storageParentID), "displayName":displayName, "storageID":storageID, "isContainer":True}
    Storage.append(type(containerName, (getContainer(containerName),), parentNameDict|properties))
    StorageIDs.append(storageID)

def addItemToStorage(itemName, storageParentID, displayName, properties, id=None):
    if id:
        storageID = id
    else:
        storageID = max(StorageIDs) + 1
    parentNameDict = {"name":itemName, "parent":int(storageParentID), "displayName":displayName, "storageID":storageID, "isContainer":False}
    Storage.append(type(itemName, (getItem(itemName),), parentNameDict|properties))
    StorageIDs.append(storageID)

def loadStorage(file):
    global StorageRoot, Storage, StorageIDs
    Storage = [StorageRoot]
    StorageIDs = [0]
    dicts = []
    for line in file.splitlines():
        dicts.append(json.loads(line))
    while len(dicts) > 0:
        for dictionary in dicts:
            if dictionary["parent"] in StorageIDs:
                if dictionary["isContainer"]:
                    addContainerToStorage(dictionary["name"],dictionary["parent"],dictionary["displayName"],dictionary,dictionary["storageID"])
                else:
                    addItemToStorage(dictionary["name"],dictionary["parent"],dictionary["displayName"],dictionary,dictionary["storageID"])
                dicts.remove(dictionary)

def addElementToTree(parent, grandparent):
    newNode = QTreeWidgetItem(grandparent)
    newNode.setText(0, str(parent.storageID))
    newNode.setText(1, parent.displayName)
    for element in Storage:
        if parent.storageID == element.parent:
            addElementToTree(element, newNode)

def loadStorageToTree(tree):
    tree.clear()
    storageTreeRoot = QTreeWidgetItem([str(StorageRoot.storageID), StorageRoot.displayName])
    tree.addTopLevelItem(storageTreeRoot)
    for element in Storage:
        if element.storageID == 0:
            continue
        if element.parent == 0:
            addElementToTree(element, storageTreeRoot)

# FILE MANAGEMENT

def newFile():
    global Containers, Items, ContainerTypes, ItemTypes, Storage, StorageIDs, currentFile, wasEdited
    Containers = [ContainerRoot]
    Items = [ItemRoot]
    Storage = [StorageRoot]
    ContainerTypes = ['root']
    ItemTypes = ['root']
    StorageIDs = [0]
    loadContainersToTree(containerTree)
    loadItemsToTree(itemTree)
    loadStorageToTree(storageTree)
    wasEdited = False
    currentFile = None
    mainWindow.setWindowTitle("BSIM - New File")

def openFile():
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
            loadStorage(zip.read("storage.txt").decode())
            loadStorageToTree(storageTree)
    global currentFile
    currentFile = selectedFile
    mainWindow.setWindowTitle(f"BSIM - {currentFile}")

def saveToFile(file):
    global wasEdited
    containerString = ""
    for container in Containers:
        if container.name == "root":
            continue
        dictionary = dict(container.__dict__)
        dictionary.pop("__module__")
        dictionary.pop("__doc__")
        containerString += json.dumps(dictionary) + "\n"
    itemString = ""
    for item in Items:
        if item.name == "root":
            continue
        dictionary = dict(item.__dict__)
        dictionary.pop("__module__")
        dictionary.pop("__doc__")
        itemString += json.dumps(dictionary) + "\n"
    storageString = ""
    for element in Storage:
        print(element.parent)
        if element.parent == None:
            continue
        dictionary = dict(element.__dict__)
        dictionary.pop("__module__")
        dictionary.pop("__doc__")
        storageString += json.dumps(dictionary) + "\n"
    with ZipFile(file, "w") as openZip:
        openZip.writestr("containers.txt", containerString)
        openZip.writestr("items.txt", itemString)
        openZip.writestr("storage.txt", storageString)
    wasEdited = False
    mainWindow.setWindowTitle(f"BSIM - {currentFile}")

def Save():
    global currentFile
    if not currentFile:
        currentFile = QFileDialog.getSaveFileUrl()[0].toString().split("//")[1]
    saveToFile(currentFile)

def SaveAs():
    currentFile = QFileDialog.getSaveFileUrl()[0].toString().split("//")[1]
    saveToFile(currentFile)

# GUI

def newContainerOpenGUI():
    loadContainersToTree(selectContainer)
    containerPropertyInput.clear()
    containerNameInput.clear()
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
    global wasEdited
    wasEdited = True
    mainWindow.setWindowTitle(f"BSIM - {currentFile}*")

def newItemOpenGUI():
    loadItemsToTree(selectItem)
    itemNameInput.clear()
    itemPropertyInput.clear()
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
    global wasEdited
    wasEdited = True
    mainWindow.setWindowTitle(f"BSIM - {currentFile}*")

def addContainerToStorageGUI():
    global addingContainer
    addingContainer = True
    loadContainersToTree(typeSelect)
    loadStorageToTree(locationSelect)
    elementNameInput.clear()
    elementPropertyInput.clear()
    addElementWindow.show()

def addItemToStorageGUI():
    global addingContainer
    addingContainer = False
    loadItemsToTree(typeSelect)
    loadStorageToTree(locationSelect)
    elementNameInput.clear()
    elementPropertyInput.clear()
    addElementWindow.show()

def loadPropertiesOfElement():
    global latestProperties
    unwanted = ["name", "storageID", "parent", "displayName"]
    propertiesList.clear()
    elementName = typeSelect.selectedItems()[0].text(0).split(":")[0]
    if addingContainer:
        element = getContainer(elementName)
    else:
        element = getItem(elementName)
    properties = dir(element)[27:]
    properties = [property for property in properties if property not in unwanted]
    propertiesList.addItems(properties)
    latestProperties = properties

def addElementToStorageProcess():
    properties = {}
    enteredProperties = elementPropertyInput.toPlainText().splitlines()
    if len(latestProperties) != len(enteredProperties):
        msg = QMessageBox()
        msg.setText("Number of properties and values do not match")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    for i in range(len(latestProperties)):
        properties[latestProperties[i]] = enteredProperties[i]
    name = elementNameInput.text()
    if not name:
        msg = QMessageBox()
        msg.setText("Element must have a name")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    location = locationSelect.selectedItems()[0].text(0)
    if not location:
        msg = QMessageBox()
        msg.setText("Element needs a location")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    elementType = typeSelect.selectedItems()[0].text(0).split(":")[0]
    if not elementType:
        msg = QMessageBox()
        msg.setText("Element needs a type")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.exec()
        return
    if addingContainer:
        addContainerToStorage(elementType,location,name,properties)
    else:
        addItemToStorage(elementType,location,name,properties)
    loadStorageToTree(storageTree)
    global wasEdited
    wasEdited = True
    mainWindow.setWindowTitle(f"BSIM - {currentFile}*")

def showProperties(item):
    element = getElementByID(int(item.text(0)))
    properties = dir(element)[27:]
    displayProperties = []
    for property in properties:
        displayProperties.append(f"{property}: {element.__dict__[property]}")
    msg = QMessageBox()
    msg.setText("\n".join(displayProperties))
    msg.setWindowTitle(element.displayName)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.exec()

# INTERFACE LOADER

addingContainer = False
wasEdited = False
currentFile = None
latestProperties = []

app = QApplication([])
uiLoader = QUiLoader()

mainWindow = uiLoader.load("../interface.ui")
newContWindow = uiLoader.load("../newCont.ui")
newItemWindow = uiLoader.load("../newItem.ui")
addElementWindow = uiLoader.load("../addToStorage.ui")

# ELEMENT DECLARATIONS

containerTree = mainWindow.findChild(QTreeWidget, "containerTree")
itemTree = mainWindow.findChild(QTreeWidget, "itemTree")
storageTree = mainWindow.findChild(QTreeWidget, "storageTree")

selectContainer = newContWindow.findChild(QTreeWidget, "contSelector")
containerNameInput = newContWindow.findChild(QLineEdit, "nameInput")
containerPropertyInput = newContWindow.findChild(QPlainTextEdit, "propertyInput")

selectItem = newItemWindow.findChild(QTreeWidget, "itemSelector")
itemNameInput = newItemWindow.findChild(QLineEdit, "nameInput")
itemPropertyInput = newItemWindow.findChild(QPlainTextEdit, "propertyInput")

locationSelect = addElementWindow.findChild(QTreeWidget, "locationSelect")
typeSelect = addElementWindow.findChild(QTreeWidget, "typeSelect")
propertiesList = addElementWindow.findChild(QListWidget, "propertiesList")
elementNameInput = addElementWindow.findChild(QLineEdit, "nameInput")
elementPropertyInput = addElementWindow.findChild(QPlainTextEdit, "propertyInput")

# SIGNAL CONNECTION

mainWindow.findChild(QAction, "actionNew_Storage").triggered.connect(newFile)
mainWindow.findChild(QAction, "actionOpen_Storage").triggered.connect(openFile)
mainWindow.findChild(QAction, "actionSave_Storage").triggered.connect(Save)
mainWindow.findChild(QAction, "actionSave_Storage_As").triggered.connect(Save)

mainWindow.findChild(QAction, "actionNew_Container").triggered.connect(newContainerOpenGUI)
mainWindow.findChild(QAction, "actionNew_Item").triggered.connect(newItemOpenGUI)

mainWindow.findChild(QAction, "actionAdd_Container").triggered.connect(addContainerToStorageGUI)
mainWindow.findChild(QAction, "actionAdd_Item").triggered.connect(addItemToStorageGUI)

newContWindow.findChild(QDialogButtonBox, "buttonBox").accepted.connect(newContainerProcess)
newItemWindow.findChild(QDialogButtonBox, "buttonBox").accepted.connect(newItemProcess)
addElementWindow.findChild(QDialogButtonBox, "buttonBox").accepted.connect(addElementToStorageProcess)

storageTree.itemDoubleClicked.connect(showProperties)

typeSelect.itemSelectionChanged.connect(loadPropertiesOfElement)

# LAUNCH

newFile()
loadStorageToTree(storageTree)
mainWindow.show()
sys.exit(app.exec())