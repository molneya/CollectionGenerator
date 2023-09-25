
from Models.Filter import Filter
from Models.Beatmap import Beatmap
from GUI.BeatmapTable import BeatmapTableView
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel
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
        self.resize(1200, 600)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.createLayout()

    def createLayout(self):
        layout = QVBoxLayout()
        self.createSearchBar(layout)
        self.createBeatmapTable(layout)
        self.createStatusLabel(layout)
        self.createCentralWidget(layout)
        self.createMenu()

    def createSearchBar(self, layout):
        horizontalLayout = QHBoxLayout()
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setPlaceholderText("Filters")
        self.searchButton = QPushButton("Filter")
        self.searchButton.clicked.connect(self.filterCollection)
        horizontalLayout.addWidget(self.searchLineEdit)
        horizontalLayout.addWidget(self.searchButton)
        layout.addLayout(horizontalLayout)

    def createBeatmapTable(self, layout):
        self.beatmapTable = BeatmapTableView(self)
        self.beatmapTable.refresh()
        layout.addWidget(self.beatmapTable)

    def createStatusLabel(self, layout):
        self.statusLabel = QLabel()
        self.updateStatusLabel()
        layout.addWidget(self.statusLabel)

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

    def updateStatusLabel(self, hidden=0):
        self.statusLabel.setText(f"Showing {self.beatmapTable.model().rowCount() - hidden} of {self.beatmapTable.model().rowCount()} beatmaps")

    def setColumnsCheckedVisible(self):
        for i, action in enumerate(self.columns):
            self.beatmapTable.setColumnHidden(i, not action.isChecked())
        self.beatmapTable.refresh()

    def filterCollection(self):
        filterText = self.searchLineEdit.text().lower()
        filters = [Filter.parse(key, Beatmap) for key in filterText.split()]
        hidden = 0
        for i, beatmap in enumerate(self.beatmapTable.model().beatmaps):
            filtered = not all(key(beatmap) for key in filters)
            self.beatmapTable.setRowHidden(i, filtered)
            hidden += int(filtered)
        self.beatmapTable.refresh()
        self.updateStatusLabel(hidden)

    def closeEvent(self, event):
        beatmaps = set(self.beatmapTable.model().beatmaps)
        self.collection.beatmaps = beatmaps
