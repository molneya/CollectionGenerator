
from Models.Config import Config
from GUI.BeatmapWindow import BeatmapWindow
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QMenu, QFileDialog
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QShortcut, QKeySequence
from functools import cmp_to_key
import locale

class CollectionTableModel(QAbstractTableModel):
    def __init__(self, collectionDatabase):
        super().__init__(None)
        self.collectionDatabase = collectionDatabase
        self.headers = ["Count", "Missing", "Name"]
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]

    def columnCount(self, parent=None):
        return len(self.headers)

    def rowCount(self, parent=None):
        return len(self.collectionDatabase)

    def data(self, index: QModelIndex, role: int):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            row = index.row()
            col = index.column()
            collection = self.collectionDatabase.collections[row]
            if col == 0: return str(len(collection))
            if col == 1: return str(collection.missing)
            if col == 2: return str(collection.name)

    def setData(self, index: QModelIndex, value, role: int):
        row = index.row()
        collection = self.collectionDatabase.collections[row]
        collection.name = value
        return True

    def sort(self, col: int, order: int):
        self.layoutAboutToBeChanged.emit()
        if   col == 0: self.collectionDatabase.collections.sort(key=lambda x: len(x))
        elif col == 1: self.collectionDatabase.collections.sort(key=lambda x: x.missing)
        elif col == 2: self.collectionDatabase.collections.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.name, y.name)))
        if order == Qt.SortOrder.DescendingOrder:
            self.collectionDatabase.collections.reverse()
        self.layoutChanged.emit()

    def flags(self, index: QModelIndex):
        if index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class CollectionTableView(QTableView):
    def __init__(self, main):
        super().__init__(None)
        self.main = main
        self.config = main.config
        self.collectionDatabase = main.collectionDatabase
        tableModel = CollectionTableModel(self.collectionDatabase)

        self.setModel(tableModel)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.createShortcuts()

    def refresh(self):
        self.clearSelection()
        self.model().layoutChanged.emit()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)

    def selectedRows(self):
        return list({selection.row() for selection in self.selectedIndexes()})

    def createShortcuts(self):
        self.viewShortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.viewShortcut.activated.connect(lambda: self.viewCollection(self.selectedRows()[0]))
        self.saveShortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.saveShortcut.activated.connect(self.saveCollections)
        self.deleteShortcut = QShortcut(QKeySequence("Delete"), self)
        self.deleteShortcut.activated.connect(self.deleteCollections)
        self.duplicateShortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.duplicateShortcut.activated.connect(self.duplicateCollections)
        self.invertShortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        self.invertShortcut.activated.connect(self.invertCollections)
        self.mergeShortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        self.mergeShortcut.activated.connect(self.mergeCollections)
        self.intersectShortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        self.intersectShortcut.activated.connect(self.intersectCollections)

    def contextMenuEvent(self, event):
        selected = self.selectedRows()
        menu = QMenu(self)

        if len(selected) == 1:
            menu.addAction("View", QKeySequence("Ctrl+P"), lambda index=selected[0]: self.viewCollection(index))
        
        menu.addAction("Save", QKeySequence("Ctrl+Shift+S"), self.saveCollections)
        menu.addAction("Delete", QKeySequence("Delete"), self.deleteCollections)
        menu.addSeparator()
        menu.addAction("Duplicate", QKeySequence("Ctrl+D"), self.duplicateCollections)
        menu.addAction("Invert", QKeySequence("Ctrl+I"), self.invertCollections)
        menu.addSeparator()

        if len(selected) == 1:
            subtract = menu.addMenu("Subtract")
            for index, collection in enumerate(self.collectionDatabase.collections):
                if selected[0] != index:
                    subtract.addAction(collection.name, lambda index=index: self.subtractCollection(index))

        if len(selected) > 1:
            menu.addAction("Merge", QKeySequence("Ctrl+M"), self.mergeCollections)
            menu.addAction("Intersect", QKeySequence("Ctrl+U"), self.intersectCollections)

        menu.popup(event.globalPos())

    def viewCollection(self, index):
        self.childWindow = BeatmapWindow(self.main, index)
        self.childWindow.show()

    def saveCollections(self):
        for index in self.selectedRows():
            collection = self.collectionDatabase.collections[index]
            filepath = QFileDialog.getSaveFileName(self, "Save Collection", f"{collection.name}.osdb", "Collection Manager Database (*.osdb);;osu! Collection Database (*.db)")[0]
            Config.backup(filepath)
            collection.save_file(filepath)

    def deleteCollections(self):
        self.collectionDatabase.delete(self.selectedRows())
        self.refresh()

    def duplicateCollections(self):
        self.collectionDatabase.duplicate(self.selectedRows(), self.config.duplicate)
        self.refresh()

    def invertCollections(self):
        self.collectionDatabase.invert(self.selectedRows(), self.config.inverse)
        self.refresh()

    def subtractCollection(self, index):
        self.collectionDatabase.subtract(self.selectedRows()[0], index, self.config.subtract)
        self.refresh()

    def mergeCollections(self):
        if not self.selectedRows():
            return
        self.collectionDatabase.merge(self.selectedRows(), self.config.merged)
        self.refresh()

    def intersectCollections(self):
        if not self.selectedRows():
            return
        self.collectionDatabase.intersect(self.selectedRows(), self.config.intersect)
        self.refresh()
