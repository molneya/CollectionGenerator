
from PyQt6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QLineEdit, QFileDialog, QPushButton, QSpinBox, QLabel
from PyQt6.QtGui import QIcon

class ConfigWindow(QWidget):
    def __init__(self, main):
        super().__init__(parent=None)
        self.config = main.config
        self.reload = main.loadConfig
        self.icon = main.icon

        self.setWindowTitle("Edit Config")
        self.setWindowIcon(self.icon)
        self.resize(600, 1)

        layout = QFormLayout()
        self.createForm(layout)
        self.setLayout(layout)

    def createForm(self, layout):
        self.createDirectorySelection(layout)
        self.createApiSelection(layout)
        self.createCollections(layout)
        self.createSaveButton(layout)

    def createDirectorySelection(self, layout):
        self.directoryLineEdit = QLineEdit()
        self.directoryLineEdit.setText(self.config.directory)
        self.directoryLineEdit.setPlaceholderText("Directory")
        self.directoryLineEdit.setReadOnly(True)
        self.directoryButton = QPushButton("Select")
        self.directoryButton.clicked.connect(self.editDirectorySelection)
        layoutHorizontal = QHBoxLayout()
        layoutHorizontal.addWidget(self.directoryLineEdit)
        layoutHorizontal.addWidget(self.directoryButton)
        layout.addRow("Directory", layoutHorizontal)

    def editDirectorySelection(self):
        directory = QFileDialog.getExistingDirectory(self, "Open osu! Directory", "")
        if directory: self.directoryLineEdit.setText(directory)

    def createApiSelection(self, layout):
        self.apiIdSpinBox = QSpinBox()
        self.apiIdSpinBox.setRange(0, 9999999)
        self.apiIdSpinBox.setValue(self.config.app_id)
        self.apiIdSpinBox.setToolTip("Application ID")
        self.apiTokenLineEdit = QLineEdit()
        self.apiTokenLineEdit.setText(self.config.app_token)
        self.apiTokenLineEdit.setPlaceholderText("Application Token")
        layoutHorizontal = QHBoxLayout()
        layoutHorizontal.addWidget(self.apiIdSpinBox)
        layoutHorizontal.addWidget(self.apiTokenLineEdit)
        layout.addRow("API Credentials", layoutHorizontal)

    def createCollections(self, layout):
        self.collectionLineEdits = []
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.bests, "Bests Collection", "Username", "osu!")
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.single, "Single Collection", "Username", "osu!", 1)
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.range, "Range Collection", "Username", "osu!", 1, 50)
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.modded, "Modded Collection", "HDDTHRFL")
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.duplicate, "Duplicated Collection", "Collection")
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.inverse, "Inverted Collection", "Collection")
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.subtract, "Subtracted Collection", "Collection1", "Collection2")
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.merged, "Merged Collection", 5)
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.intersect, "Intersected Collection", 5)
        self.createCollectionSelection(layout, self.collectionLineEdits, self.config.leeways, "Leeways Collection", 1.9, 2.0, "DTHR")

    def createCollectionSelection(self, layout, lineEditList, config, hint, *format):
        collectionLineEdit = QLineEdit()
        collectionLineEdit.setText(config)
        collectionLineEdit.setPlaceholderText(hint)
        collectionLineEdit.setFixedWidth(300)
        lineEditList.append(collectionLineEdit)
        collectionPreview = QLabel()
        collectionPreview.setText("Meow :3c")
        collectionLineEdit.textEdited.connect(lambda: self.editCollectionPreview(collectionLineEdit, collectionPreview, *format))
        self.editCollectionPreview(collectionLineEdit, collectionPreview, *format)
        layoutHorizontal = QHBoxLayout()
        layoutHorizontal.addWidget(collectionLineEdit)
        layoutHorizontal.addWidget(collectionPreview)
        layout.addRow(hint, layoutHorizontal)

    def editCollectionPreview(self, collectionLineEdit, collectionPreview, *format):
        try:
            preview = collectionLineEdit.text().format(*format)
            collectionPreview.setText(preview)
        except:
            collectionPreview.setText("<font color=\"#F00\">Invalid Collection Name</font>")

    def createSaveButton(self, layout):
        self.saveButton = QPushButton("Save and Reload")
        self.saveButton.clicked.connect(self.saveConfig)
        layout.addRow(self.saveButton)

    def saveConfig(self):
        self.config.directory = self.directoryLineEdit.text()
        self.config.app_id = self.apiIdSpinBox.value()
        self.config.app_token = self.apiTokenLineEdit.text()
        self.config.bests = self.collectionLineEdits[0].text()
        self.config.single = self.collectionLineEdits[1].text()
        self.config.range = self.collectionLineEdits[2].text()
        self.config.modded = self.collectionLineEdits[3].text()
        self.config.duplicate = self.collectionLineEdits[4].text()
        self.config.inverse = self.collectionLineEdits[5].text()
        self.config.subtract = self.collectionLineEdits[6].text()
        self.config.merged = self.collectionLineEdits[7].text()
        self.config.intersect = self.collectionLineEdits[8].text()
        self.config.leeways = self.collectionLineEdits[9].text()
        self.config.save()
        self.reload()
