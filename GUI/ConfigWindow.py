
from PyQt6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QFileDialog, QPushButton, QSpinBox, QLabel, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ConfigWindow(QWidget):
    def __init__(self, main):
        super().__init__(parent=None)
        self.config = main.config
        self.reload = main.loadConfig
        self.icon = main.icon

        self.setWindowTitle("Edit Config")
        self.setWindowIcon(self.icon)
        self.setFixedWidth(700)
        self.setWindowFlags(Qt.WindowType.Dialog)

        layout = QVBoxLayout()
        self.createSettingsBox(layout)
        self.createCollectionsBox(layout)
        self.createSaveButton(layout)
        self.setLayout(layout)

    def createSettingsBox(self, layout):
        settingsBox = QGroupBox("Settings")
        settingsLayout = QFormLayout()
        self.createDirectorySelection(settingsLayout)
        self.createApiSelection(settingsLayout)
        settingsBox.setLayout(settingsLayout)
        layout.addWidget(settingsBox)

    def createCollectionsBox(self, layout):
        collectionsBox = QGroupBox("Generated Collection Names")
        collectionLayout = QFormLayout()
        self.createCollections(collectionLayout)
        collectionsBox.setLayout(collectionLayout)
        layout.addWidget(collectionsBox)

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
        tooltip = "<p>You can find this by:<ol><li>Going into your <b>account settings</b> on osu.ppy.sh</li><li>Scrolling down to <b>OAuth</b></li><li>Creating a <b>New OAuth Application</b> if you don't already have one (set whatever name)</li><li>Copying the <b>Client ID</b> and <b>Client Secret</b> into these fields</li></ol></p>"
        self.apiIdSpinBox = QSpinBox()
        self.apiIdSpinBox.setRange(0, 9999999)
        self.apiIdSpinBox.setValue(self.config.app_id)
        self.apiIdSpinBox.setToolTip(tooltip)
        self.apiTokenLineEdit = QLineEdit()
        self.apiTokenLineEdit.setText(self.config.app_token)
        self.apiTokenLineEdit.setPlaceholderText("Client Secret")
        self.apiTokenLineEdit.setToolTip(tooltip)
        self.apiTokenLineEdit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        layoutHorizontal = QHBoxLayout()
        layoutHorizontal.addWidget(self.apiIdSpinBox)
        layoutHorizontal.addWidget(self.apiTokenLineEdit)
        credentialsLabel = QLabel("OAuth Credentials")
        credentialsLabel.setToolTip(tooltip)
        layout.addRow(credentialsLabel, layoutHorizontal)

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
        layout.addWidget(self.saveButton)

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
