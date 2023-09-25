
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QMenu
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QShortcut, QKeySequence
from functools import cmp_to_key
import locale

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
            if col == 0: return beatmap.artist
            if col == 1: return beatmap.title
            if col == 2: return beatmap.creator
            if col == 3: return beatmap.version
            if col == 4: return beatmap.hash
            if col == 5: return beatmap.status
            if col == 6: return beatmap.circles
            if col == 7: return beatmap.sliders
            if col == 8: return beatmap.spinners
            if col == 9: return beatmap.ar
            if col == 10: return beatmap.cs
            if col == 11: return beatmap.hp
            if col == 12: return beatmap.od
            if col == 13: return beatmap.drain
            if col == 14: return beatmap.length
            if col == 15: return beatmap.beatmap_id
            if col == 16: return beatmap.beatmapset_id
            if col == 17: return beatmap.mode
            if col == 18: return beatmap.source
            if col == 19: return beatmap.missing

    def sort(self, col: int, order: int):
        self.layoutAboutToBeChanged.emit()
        if   col == 0: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.artist, y.artist)))
        elif col == 1: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.title, y.title)))
        elif col == 2: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.creator, y.creator)))
        elif col == 3: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.version, y.version)))
        elif col == 4: self.beatmaps.sort(key=lambda x: x.hash)
        elif col == 5: self.beatmaps.sort(key=lambda x: x.status)
        elif col == 6: self.beatmaps.sort(key=lambda x: x.circles)
        elif col == 7: self.beatmaps.sort(key=lambda x: x.sliders)
        elif col == 8: self.beatmaps.sort(key=lambda x: x.spinners)
        elif col == 9: self.beatmaps.sort(key=lambda x: x.ar)
        elif col == 10: self.beatmaps.sort(key=lambda x: x.cs)
        elif col == 11: self.beatmaps.sort(key=lambda x: x.hp)
        elif col == 12: self.beatmaps.sort(key=lambda x: x.od)
        elif col == 13: self.beatmaps.sort(key=lambda x: x.drain)
        elif col == 14: self.beatmaps.sort(key=lambda x: x.length)
        elif col == 15: self.beatmaps.sort(key=lambda x: x.beatmap_id)
        elif col == 16: self.beatmaps.sort(key=lambda x: x.beatmapset_id)
        elif col == 17: self.beatmaps.sort(key=lambda x: x.mode)
        elif col == 18: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.source, y.source)))
        elif col == 19: self.beatmaps.sort(key=lambda x: x.missing)
        if order == Qt.SortOrder.DescendingOrder:
            self.beatmaps.reverse()
        self.layoutChanged.emit()

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class BeatmapTableView(QTableView):
    def __init__(self, collection):
        super().__init__(None)
        tableModel = BeatmapTableModel(collection)
        self.setModel(tableModel)
        self.setSortingEnabled(True)
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
