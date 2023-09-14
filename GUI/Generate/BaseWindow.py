
from Models.Filter import Filter
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QProgressDialog, QApplication, QCheckBox, QComboBox, QHBoxLayout, QSpinBox, QMessageBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6 import QtTest

class GenerateBaseWindow(QWidget):
    def __init__(self, main, name="This text should not appear"):
        super().__init__(parent=None)
        self.config = main.config
        self.ossapi = main.ossapi
        self.collectionDatabase = main.collectionDatabase
        self.collectionTable = main.collectionTable
        self.icon = main.icon
        self.name = name
        self.generateProgress = None

        self.setWindowTitle(self.name)
        self.setWindowIcon(self.icon)
        self.resize(400, 1)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)

        layout = QFormLayout()
        self.createForm(layout)
        self.setLayout(layout)

    @classmethod
    def create(cls, main):
        return cls(main)

    def closeEvent(self, event):
        if self.generateProgress:
            self.generateProgress.close()

    def wait(self, milliseconds: int):
        QtTest.QTest.qWait(milliseconds)

    def createForm(self, layout):
        pass

    def generateCollection(self):
        pass

    def createUsername(self, layout):
        self.usernameLineEdit = QLineEdit()
        self.usernameLineEdit.setPlaceholderText("Username")
        layout.addRow("Username", self.usernameLineEdit)

    def getUsername(self):
        return self.usernameLineEdit.text()

    def createMode(self, layout):
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItems(["osu!", "osu!taiko", "osu!catch", "osu!mania"])
        layout.addRow("Mode", self.modeComboBox)

    def getMode(self):
        return self.modeComboBox.currentText()

    def getOssapiMode(self):
        mode = self.getMode()
        if mode == "osu!": return "osu"
        if mode == "osu!taiko": return "taiko"
        if mode == "osu!catch": return "fruits"
        if mode == "osu!mania": return "mania"

    def getIntMode(self):
        return self.modeComboBox.currentIndex()

    def createSeparateMods(self, layout):
        self.separateModsCheckBox = QCheckBox("Generate collection for each mod")
        self.includeVisualCheckBox = QCheckBox("Include preference mods? (SD/PF/NC/MR)")
        self.separateModsCheckBox.setChecked(True)
        self.separateModsCheckBox.toggled.connect(self.onSeparateModsChange)
        self.includeVisualCheckBox.setEnabled(True)
        layout.addRow(self.separateModsCheckBox)
        layout.addRow(self.includeVisualCheckBox)

    def onSeparateModsChange(self, toggled):
        self.includeVisualCheckBox.setEnabled(toggled)

    def getSeparateMods(self):
        return self.separateModsCheckBox.isChecked()

    def getIncludeVisual(self):
        return self.includeVisualCheckBox.isChecked()

    def createRanks(self, layout):
        layoutRank = QHBoxLayout()
        self.rankMinSpinBox = QSpinBox()
        self.rankMinSpinBox.setMinimum(1)
        self.rankMinSpinBox.setMaximum(100)
        self.rankMinSpinBox.setSingleStep(1)
        self.rankMinSpinBox.setValue(1)
        self.rankMinSpinBox.editingFinished.connect(self.onRankMinEdit)
        self.rankMaxSpinBox = QSpinBox()
        self.rankMaxSpinBox.setMinimum(1)
        self.rankMaxSpinBox.setMaximum(100)
        self.rankMaxSpinBox.setSingleStep(1)
        self.rankMaxSpinBox.setValue(50)
        self.rankMaxSpinBox.editingFinished.connect(self.onRankMaxEdit)
        layoutRank.addWidget(self.rankMinSpinBox)
        layoutRank.addWidget(self.rankMaxSpinBox)
        layout.addRow("Rank Range", layoutRank)

    def onRankMinEdit(self):
        minValue = self.rankMinSpinBox.value()
        maxValue = self.rankMaxSpinBox.value()
        if minValue > maxValue:
            self.rankMinSpinBox.setValue(maxValue)

    def onRankMaxEdit(self):
        minValue = self.rankMinSpinBox.value()
        maxValue = self.rankMaxSpinBox.value()
        if maxValue < minValue:
            self.rankMaxSpinBox.setValue(minValue)

    def getRankMin(self):
        return self.rankMinSpinBox.value()

    def getRankMax(self):
        return self.rankMaxSpinBox.value()

    def createFilters(self, layout, model):
        self.filtersLineEdit = QLineEdit()
        self.filtersLineEdit.setPlaceholderText("Filters")
        parameters = ', '.join(sorted([f"{key} ({type.__name__})" for key, type in model.__annotations__.items() if type in [float, int, bool, str]]))
        self.filtersLineEdit.setToolTip(f"<p>Use filters just like you would in osu!. A filter without comparators searches tags instead. When filtering strings, use <code>==</code> for exact matches, and <code>=</code> for partial matches.</p><p><b>Possible filters:</b> {parameters}</p>")
        layout.addRow("Filters", self.filtersLineEdit)

    def getFilterName(self):
        return self.filtersLineEdit.text().lower()

    def getFilters(self, model):
        filters = self.filtersLineEdit.text().lower()
        return [Filter.parse(key, model) for key in filters.split()]

    def createLeewayMods(self, layout):
        self.modsComboBox = QComboBox()
        self.modsComboBox.addItems(["DTHR", "DT", "HR", "EZ", "HT", "EZHT"])
        layout.addRow("Mods", self.modsComboBox)

    def getLeewayMods(self):
        return self.modsComboBox.currentText()

    def createCollection(self, layout):
        self.collectionComboBox = QComboBox()
        self.collectionComboBox.addItems([collection.name for collection in self.collectionDatabase.collections])
        layout.addRow("Collection", self.collectionComboBox)

    def getCollectionIndex(self):
        return self.collectionComboBox.currentIndex()

    def getCollection(self):
        index = self.getCollectionIndex()
        return self.collectionDatabase.collections[index]

    def createGenerateProgress(self, count):
        self.progress = 0
        self.generateProgress = QProgressDialog("Collecting beatmaps...", "Cancel", 0, count)
        self.generateProgress.setWindowTitle(self.name)
        self.generateProgress.setWindowIcon(self.icon)
        self.generateProgress.setValue(self.progress)
        self.generateProgress.show()
        QApplication.processEvents()

    def updateGenerateProgress(self):
        self.progress += 1
        self.generateProgress.setValue(self.progress)
        QApplication.processEvents()
        if self.generateProgress.wasCanceled():
            self.generateProgress.close()
            return False
        return True

    def createGenerateButton(self, layout):
        self.generatePushButton = QPushButton("Generate")
        self.generatePushButton.clicked.connect(self.generateCollection)
        layout.addRow(self.generatePushButton)
