
from Models.Config import Config
from Models.CollectionDatabase import CollectionDatabase
from GUI.ConfigWindow import ConfigWindow
from GUI.CollectionTable import CollectionTableView
from GUI.Generate.BestsWindow import GenerateBestsWindow
from GUI.Generate.FilterBeatmapsWindow import GenerateFilterBeatmapsWindow
from GUI.Generate.FilterScoresWindow import GenerateFilterScoresWindow
from GUI.Generate.FirstsCountryWindow import GenerateFirstsCountryWindow
from GUI.Generate.FirstsGlobalWindow import GenerateFirstsGlobalWindow
from GUI.Generate.LeaderboardsWindow import GenerateLeaderboardsWindow
from GUI.Generate.LeewaysWindow import GenerateLeewaysWindow
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QFileDialog, QLabel, QMessageBox
from PyQt6.QtGui import QIcon, QKeySequence
from importlib import import_module
from ossapi import Ossapi
import sys
import os

class MainWindow(QMainWindow):
    name = "Collection Generator"
    version = "v20230915.1"

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle(self.name)
        self.resize(500, 600)
        self.setAcceptDrops(True)

        try: self.icon = QIcon(os.path.join(sys._MEIPASS, "files/icon.png"))
        except: self.icon = QIcon("files/icon.png")
        self.setWindowIcon(self.icon)

        self.collectionDatabase = CollectionDatabase()
        self.config = Config()
        self.ossapi = None

        self.childWindow = None
        self.createLayout()
        self.loadConfig()

    def createLayout(self):
        layout = QVBoxLayout()
        self.createCollectionTable(layout)
        self.createStatusLabel(layout)
        self.createCentralWidget(layout)
        self.createMenu()

    def createCollectionTable(self, layout):
        self.collectionTable = CollectionTableView(self)
        layout.addWidget(self.collectionTable)
        self.collectionTable.refresh()

    def createStatusLabel(self, layout):
        self.statusLabel = QLabel()
        layout.addWidget(self.statusLabel)

    def createCentralWidget(self, layout):
        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def createMenu(self):
        fileMenu = self.menuBar().addMenu("File")
        fileMenu.addAction("New", QKeySequence("Ctrl+N"), self.clearCollection)
        openMenu = fileMenu.addMenu("Open")
        openMenu.addAction("File", QKeySequence("Ctrl+O"), self.loadCollection)
        openMenu.addAction("osu! Collection", QKeySequence("Ctrl+Alt+O"), self.loadOsuCollection)
        saveMenu = fileMenu.addMenu("Save")
        saveMenu.addAction("File", QKeySequence("Ctrl+S"), self.saveCollection)
        saveMenu.addAction("osu! Collection", QKeySequence("Ctrl+Alt+S"), self.saveOsuCollection)
        fileMenu.addAction("Exit", QKeySequence("Alt+F4"), self.close)
        createMenu = self.menuBar().addMenu("Generate")
        createMenu.addAction("Bests", QKeySequence("Ctrl+1"), lambda: self.createWindow(GenerateBestsWindow))
        filterMenu = createMenu.addMenu("Filter")
        filterMenu.addAction("Beatmaps", QKeySequence("Ctrl+2"), lambda: self.createWindow(GenerateFilterBeatmapsWindow))
        filterMenu.addAction("Scores", QKeySequence("Ctrl+3"), lambda: self.createWindow(GenerateFilterScoresWindow))
        firstsMenu = createMenu.addMenu("Firsts")
        firstsMenu.addAction("Country", QKeySequence("Ctrl+4"), lambda: self.createWindow(GenerateFirstsCountryWindow))
        firstsMenu.addAction("Global", QKeySequence("Ctrl+5"), lambda: self.createWindow(GenerateFirstsGlobalWindow))
        createMenu.addAction("Leaderboards", QKeySequence("Ctrl+6"), lambda: self.createWindow(GenerateLeaderboardsWindow))
        createMenu.addAction("Leeways", QKeySequence("Ctrl+7"), lambda: self.createWindow(GenerateLeewaysWindow))
        self.menuBar().addAction("Config", QKeySequence("Ctrl+E"), lambda: self.createWindow(ConfigWindow))
        self.menuBar().addAction("About", self.about)

    def createWindow(self, Module):
        if self.childWindow:
            self.childWindow.close()
        try:
            self.childWindow = Module(self)
            self.childWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Exception", str(e))

    def loadConfig(self):
        self.config.load()
        if self.collectionDatabase.database.is_empty():
            self.loadCollectionDatabase()
        self.loadOssapi()

    def loadOssapi(self):
        if not self.config.app_token or not self.config.app_id:
            self.ossapi = None
            return
        try:
            self.ossapi = Ossapi(self.config.app_id, self.config.app_token)
        except Exception as e:
            QMessageBox.critical(self, "Exception", str(e))
            self.ossapi = None

    def loadCollectionDatabase(self):
        self.statusLabel.setText("Loading database...")
        if not self.config.directory:
            self.statusLabel.setText("To set up, open <code>Config</code> and select your osu! directory")
            return
        try:
            filepath = os.path.join(self.config.directory, "osu!.db")
            self.collectionDatabase.load_database(filepath)
            self.statusLabel.setText(f"Successfully loaded {len(self.collectionDatabase.database):,} beatmaps from database")
        except Exception as e:
            self.statusLabel.setText("Failed to load database")
            QMessageBox.critical(self, "Exception", str(e))
            return

    def loadCollectionFilepath(self, filepath):
        try:
            self.collectionDatabase.load_file(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Exception", str(e))

    def loadCollection(self):
        filepath = QFileDialog.getOpenFileName(self, "Open Collection", "", "Collection Manager Database (*.osdb);;osu! Collection Database (*.db);;Text Files (*.txt);;All Files (*.*)")[0]
        self.loadCollectionFilepath(filepath)
        self.collectionTable.refresh()

    def loadOsuCollection(self):
        try:
            filepath = os.path.join(self.config.directory, "collection.db")
            self.loadCollectionFilepath(filepath)
            self.collectionTable.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Exception", str(e))

    def dropEvent(self, event):
        filepaths = [url.toLocalFile() for url in event.mimeData().urls()]
        for filepath in filepaths:
            self.loadCollectionFilepath(filepath)
        self.collectionTable.refresh()

    def saveCollection(self):
        filepath = QFileDialog.getSaveFileName(self, "Save Collection", "", "Collection Manager Database (*.osdb);;osu! Collection Database (*.db)")[0]
        Config.backup(filepath)
        self.collectionDatabase.save_file(filepath)

    def saveOsuCollection(self):
        try:
            filepath = os.path.join(self.config.directory, "collection.db")
            Config.backup(filepath)
            self.collectionDatabase.save_file(filepath)
            QMessageBox.information(self, "Save", "Saved osu! collection")
        except Exception as e:
            QMessageBox.critical(self, "Exception", str(e))

    def clearCollection(self):
        if len(self.collectionDatabase) > 0:
            button = QMessageBox.question(self, "Confirm", "You have open collections! Are you sure you want to continue?")
            if button == QMessageBox.StandardButton.No:
                return

        self.collectionDatabase.clear()
        self.collectionTable.refresh()

    def closeEvent(self, event):
        if len(self.collectionDatabase) > 0:
            button = QMessageBox.question(self, "Confirm", "You have open collections! Are you sure you want to exit?")
            if button == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self.collectionTable.closeEvent(event)
        if self.childWindow:
            self.childWindow.close()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def about(self):
        QMessageBox.about(self, self.name, f"<h4>About {self.name} {self.version}</h4><p>Tops and firsts data from <a href=\"https://osu.ppy.sh/home\">osu.ppy.sh</a> by <a href=\"https://osu.ppy.sh/users/2\">peppy</a></p><p>Country data from <a href=\"https://snipe.huismetbenen.nl\">snipe.huismetbenen.nl</a> by <a href=\"https://osu.ppy.sh/users/2330619\">Mr HeliX</a></p><p>Leaderboard data from <a href=\"https://osustats.ppy.sh/\">osustats.ppy.sh</a> by <a href=\"https://osu.ppy.sh/users/304520\">Piotrekol</a> and <a href=\"https://osu.ppy.sh/users/1231180\">Ezoda</a></p><p>Program created by <a href=\"https://osu.ppy.sh/users/8945180\">molneya</a></p><p>View and download source code and releases on <a href=\"https://github.com/molneya/CollectionGenerator\">GitHub</a></p>")
