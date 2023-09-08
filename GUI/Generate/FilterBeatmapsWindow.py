
from Models.Beatmap import Beatmap
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox

class GenerateFilterBeatmapsWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Filter Beatmaps")

    @classmethod
    def create(cls, main):
        if main.collectionDatabase.database.is_empty():
            QMessageBox.critical(main, "Error", "<p>Config error: osu!.db not loaded!</p><p>Please edit and reload your config before using this feature.</p>")
            return
        return cls(main)

    def createForm(self, layout):
        self.createFilters(layout, Beatmap)
        self.createGenerateButton(layout)

    def generateCollection(self):
        beatmaps = self.collectionDatabase.database.beatmaps()
        for key in self.getFilters(Beatmap):
            beatmaps = filter(key, beatmaps)

        name = self.getFilterName()
        beatmaps = set(beatmaps)
        self.collectionDatabase.append(Collection(name, beatmaps))

        self.collectionTable.refresh()
