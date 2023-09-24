
from GUI.BeatmapTable import BeatmapTableView
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

class BeatmapWindow(QWidget):
    def __init__(self, main, index):
        super().__init__(parent=None)
        self.main = main
        self.icon = main.icon
        self.collection = main.collectionDatabase.collections[index]

        self.setWindowTitle(self.collection.name)
        self.setWindowIcon(self.icon)
        self.resize(1000, 600)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.createLayout()

    def createLayout(self):
        layout = QVBoxLayout()
        self.createBeatmapTable(layout)
        self.setLayout(layout)

    def createBeatmapTable(self, layout):
        self.beatmapTable = BeatmapTableView(self.collection)
        self.beatmapTable.refresh()
        layout.addWidget(self.beatmapTable)
