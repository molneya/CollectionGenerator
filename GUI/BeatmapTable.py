
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QMenu
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel, QUrl
from PyQt6.QtGui import QShortcut, QKeySequence, QDesktopServices
from functools import cmp_to_key
import locale

class BeatmapTableModel(QAbstractTableModel):
    def __init__(self, collection):
        super().__init__(None)
        self.beatmaps = list(collection.beatmaps)
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
            if col == 0: return beatmap.name()
            if col == 1: return beatmap.artist
            if col == 2: return beatmap.title
            if col == 3: return beatmap.creator
            if col == 4: return beatmap.version
            if col == 5: return beatmap.hash
            if col == 6: return beatmap.status
            if col == 7: return beatmap.circles
            if col == 8: return beatmap.sliders
            if col == 9: return beatmap.spinners
            if col == 10: return beatmap.ar
            if col == 11: return beatmap.cs
            if col == 12: return beatmap.hp
            if col == 13: return beatmap.od
            if col == 14: return beatmap.drain
            if col == 15: return beatmap.length
            if col == 16: return beatmap.beatmap_id
            if col == 17: return beatmap.beatmapset_id
            if col == 18: return beatmap.mode
            if col == 19: return beatmap.source
            if col == 20: return beatmap.missing

    def sort(self, col: int, order: int):
        self.layoutAboutToBeChanged.emit()
        if   col == 0: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.name(), y.name())))
        elif col == 1: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.artist, y.artist)))
        elif col == 2: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.title, y.title)))
        elif col == 3: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.creator, y.creator)))
        elif col == 4: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.version, y.version)))
        elif col == 5: self.beatmaps.sort(key=lambda x: x.hash)
        elif col == 6: self.beatmaps.sort(key=lambda x: x.status)
        elif col == 7: self.beatmaps.sort(key=lambda x: x.circles)
        elif col == 8: self.beatmaps.sort(key=lambda x: x.sliders)
        elif col == 9: self.beatmaps.sort(key=lambda x: x.spinners)
        elif col == 10: self.beatmaps.sort(key=lambda x: x.ar)
        elif col == 11: self.beatmaps.sort(key=lambda x: x.cs)
        elif col == 12: self.beatmaps.sort(key=lambda x: x.hp)
        elif col == 13: self.beatmaps.sort(key=lambda x: x.od)
        elif col == 14: self.beatmaps.sort(key=lambda x: x.drain)
        elif col == 15: self.beatmaps.sort(key=lambda x: x.length)
        elif col == 16: self.beatmaps.sort(key=lambda x: x.beatmap_id)
        elif col == 17: self.beatmaps.sort(key=lambda x: x.beatmapset_id)
        elif col == 18: self.beatmaps.sort(key=lambda x: x.mode)
        elif col == 19: self.beatmaps.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.source, y.source)))
        elif col == 20: self.beatmaps.sort(key=lambda x: x.missing)
        if order == Qt.SortOrder.DescendingOrder:
            self.beatmaps.reverse()
        self.layoutChanged.emit()

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class BeatmapTableView(QTableView):
    def __init__(self, main):
        super().__init__(None)
        self.main = main
        tableModel = BeatmapTableModel(main.collection)
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
        self.openShortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.openShortcut.activated.connect(self.openBeatmaps)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Delete", QKeySequence("Delete"), self.deleteBeatmaps)
        menu.addAction("Open", QKeySequence("Ctrl+P"), self.openBeatmaps)
        menu.popup(event.globalPos())

    def deleteBeatmaps(self):
        selected = self.selectedRows()
        for row in selected[::-1]:
            self.model().beatmaps.pop(row)
        self.refresh()
        self.main.updateStatusLabel()

    def openBeatmaps(self):
        sets = []
        beatmaps = []
        for row in self.selectedRows():
            beatmap = self.model().beatmaps[row]
            if beatmap.beatmapset_id != 0:
                if beatmap.beatmapset_id not in sets:
                    sets.append(beatmap.beatmapset_id)
            # If we don't have a set_id, fall back to beatmap_id
            elif beatmap.beatmap_id != 0:
                if beatmap.beatmap_id not in beatmaps:
                    beatmaps.append(beatmap.beatmap_id)

        # Open URLs in browser
        for id in sets:
            url = QUrl(f"https://osu.ppy.sh/s/{id}")
            QDesktopServices.openUrl(url)
        for id in beatmaps:
            url = QUrl(f"https://osu.ppy.sh/b/{id}")
            QDesktopServices.openUrl(url)
