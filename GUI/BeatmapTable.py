
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QMenu
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QShortcut, QKeySequence

class BeatmapTableModel(QAbstractTableModel):
    def __init__(self, collection):
        super().__init__(None)
        self.beatmaps = list(collection.beatmaps)
        self.headers = [
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
            indexes = [
                beatmap.artist,
                beatmap.title,
                beatmap.creator,
                beatmap.version,
                beatmap.hash,
                beatmap.status,
                beatmap.circles,
                beatmap.sliders,
                beatmap.spinners,
                beatmap.ar,
                beatmap.cs,
                beatmap.hp,
                beatmap.od,
                beatmap.drain,
                beatmap.length,
                beatmap.beatmap_id,
                beatmap.beatmapset_id,
                beatmap.mode,
                beatmap.source,
                beatmap.missing,
            ]
            return indexes[col]

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class BeatmapTableView(QTableView):
    def __init__(self, collection):
        super().__init__(None)
        tableModel = BeatmapTableModel(collection)
        self.setModel(tableModel)
        self.setSortingEnabled(False)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.createShortcuts()

    def refresh(self):
        self.clearSelection()
        self.model().layoutChanged.emit()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def selectedRows(self):
        return list({selection.row() for selection in self.selectedIndexes()})

    def createShortcuts(self):
        self.deleteShortcut = QShortcut(QKeySequence("Delete"), self)
        self.deleteShortcut.activated.connect(self.deleteBeatmaps)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Delete", self.deleteBeatmaps)
        menu.popup(event.globalPos())

    def deleteBeatmaps(self):
        selected = self.selectedRows()
        for row in selected[::-1]:
            self.model().beatmaps.pop(row)
        self.refresh()
