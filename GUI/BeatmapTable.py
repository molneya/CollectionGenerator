
from PyQt6.QtWidgets import QTableView, QAbstractItemView
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel

class BeatmapTableModel(QAbstractTableModel):
    def __init__(self, collectionDatabase):
        super().__init__(None)
        self.collectionDatabase = collectionDatabase
        self.beatmaps = []
        self.headers = ["Artist", "Title", "Creator", "Version"]

    def setBeatmaps(self, index: QModelIndex):
        row = index.row()
        self.beatmaps = list(self.collectionDatabase.collections[row].beatmaps)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]

    def columnCount(self, parent=None):
        return len(self.headers)

    def rowCount(self, parent=None):
        return len(self.beatmaps)

    def data(self, index: QModelIndex, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            beatmap = self.beatmaps[row]
            if col == 0: return beatmap.artist
            if col == 1: return beatmap.title
            if col == 2: return beatmap.creator
            if col == 3: return beatmap.version

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class BeatmapTableView(QTableView):
    def __init__(self, main):
        super().__init__(None)
        self.main = main
        self.collectionDatabase = main.collectionDatabase

        tableModel = BeatmapTableModel(self.collectionDatabase)
        self.setModel(tableModel)
        self.setSortingEnabled(False)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def updateIndex(self, index: QModelIndex):
        self.model().setBeatmaps(index)
        self.refresh()

    def refresh(self):
        self.clearSelection()
        self.model().layoutChanged.emit()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
