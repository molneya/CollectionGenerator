
from Models.Config import Config
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QMenu, QFileDialog, QShortcut
from PyQt6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt6.QtGui import QKeySequence
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
        if col == 0: self.collectionDatabase.collections.sort(key=lambda x: len(x))
        if col == 1: self.collectionDatabase.collections.sort(key=lambda x: x.missing)
        if col == 2: self.collectionDatabase.collections.sort(key=cmp_to_key(lambda x, y: locale.strcoll(x.name, y.name)))
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

    def createShortcuts(self):
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
        rows = list(set([selection.row() for selection in self.selectedIndexes()]))
        menu = QMenu(self)
        menu.addAction("Save", lambda: self.saveCollections(rows))
        menu.addAction("Delete", lambda: self.deleteCollections(rows))
        menu.addSeparator()
        menu.addAction("Duplicate", lambda: self.duplicateCollections(rows))
        menu.addAction("Invert", lambda: self.invertCollections(rows))
        menu.addSeparator()

        if len(rows) == 1:
            subtract = menu.addMenu("Subtract")
            for index, collection in enumerate(self.collectionDatabase.collections):
                if rows[0] != index:
                    subtract.addAction(collection.name, lambda index=index: self.subtractCollections(rows[0], index))

        if len(rows) > 1:
            menu.addAction("Merge", lambda: self.mergeCollections(rows))
            menu.addAction("Intersect", lambda: self.intersectCollections(rows))

        menu.popup(event.globalPos())

    def saveCollections(self, indices):
        for index in indices:
            collection = self.collectionDatabase.collections[index]
            filepath = QFileDialog.getSaveFileName(self, "Save Collection", f"{collection.name}.osdb", "Collection Manager Database (*.osdb);;osu! Collection Database (*.db)")[0]
            Config.backup(filepath)
            collection.save_file(filepath)

    def deleteCollections(self, indices):
        self.collectionDatabase.delete(indices)
        self.refresh()

    def duplicateCollections(self, indices):
        self.collectionDatabase.duplicate(indices, self.config.duplicate)
        self.refresh()

    def invertCollections(self, indices):
        self.collectionDatabase.invert(indices, self.config.inverse)
        self.refresh()

    def subtractCollections(self, index1, index2):
        self.collectionDatabase.subtract(index1, index2, self.config.subtract)
        self.refresh()

    def mergeCollections(self, indices):
        self.collectionDatabase.merge(indices, self.config.merged)
        self.refresh()

    def intersectCollections(self, indices):
        self.collectionDatabase.intersect(indices, self.config.intersect)
        self.refresh()
