
from GUI.BeatmapTable import BeatmapTableView
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt

class BeatmapWindow(QMainWindow):
    def __init__(self, main, index):
        super().__init__(parent=None)
        self.icon = main.icon
        self.collection = main.collectionDatabase.collections[index]
        self.headers = [
            "Name",
            "Artist",
            "Title",
            "Creator",
            "Version",
            "Hash",
            "Status",
            "Circles",
            "Sliders",
            "Spinners",
            "AR",
            "CS",
            "HP",
            "OD",
            "Drain",
            "Length",
            "Beatmap ID",
            "Beatmapset ID",
            "Mode",
            "Source",
            "Missing",
        ]
        self.defaultHeaders = [
            "Name",
            "Status",
            "Circles",
            "Sliders",
            "Spinners",
            "AR",
            "CS",
            "HP",
            "OD",
            "Mode",
            "Missing",
        ]

        self.setWindowTitle(self.collection.name)
        self.setWindowIcon(self.icon)
        self.resize(1000, 600)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.createLayout()

    def createLayout(self):
        layout = QVBoxLayout()
        self.createBeatmapTable(layout)
        self.createCentralWidget(layout)
        self.createMenu()

    def createBeatmapTable(self, layout):
        self.beatmapTable = BeatmapTableView(self.collection)
        self.beatmapTable.refresh()
        layout.addWidget(self.beatmapTable)

    def createCentralWidget(self, layout):
        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def createMenu(self):
        fileMenu = self.menuBar().addMenu("File")
        fileMenu.addAction("Exit", QKeySequence("Alt+F4"), self.close)
        viewMenu = self.menuBar().addMenu("View")
        self.columns = [QAction(header, checkable=True, checked=header in self.defaultHeaders) for header in self.headers]
        self.setColumnsCheckedVisible()
        for action in self.columns:
            viewMenu.addAction(action)
        viewMenu.triggered.connect(self.setColumnsCheckedVisible)

    def setColumnsCheckedVisible(self):
        for i, action in enumerate(self.columns):
            self.beatmapTable.setColumnHidden(i, not action.isChecked())
        self.beatmapTable.refresh()
