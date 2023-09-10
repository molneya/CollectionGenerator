
from Models.Collection import Collection
from Models.BeatmapParser import BeatmapParser
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox
import os

class GenerateLeewaysWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Leeways")

    @classmethod
    def create(cls, main):
        if main.collectionDatabase.database.is_empty():
            QMessageBox.critical(main, "Error", "<p>Config error: osu!.db not loaded!</p><p>Please edit and reload your config before using this feature.</p>")
            return
        if len(main.collectionDatabase) == 0:
            QMessageBox.critical(main, "Error", "<p>Collection error: No collections loaded!</p><p>Please load a collection before using this feature.</p>")
            return
        return cls(main)

    def createForm(self, layout):
        self.createCollection(layout)
        self.createLeewayMods(layout)
        self.createGenerateButton(layout)

    def calculateLeeways(self, beatmaps, mods):
        count = len(beatmaps)
        self.createGenerateProgress(count)

        # Calculate leeways per beatmap
        for beatmap in beatmaps:
            if beatmap.leeway < 0:
                filename = os.path.join(self.config.directory, "Songs", beatmap.foldername, beatmap.filename)
                beatmapParser = BeatmapParser.from_file(filename)
                leeway = min(beatmapParser.get_leeways(mods) or [-1])
                beatmap.leeway = leeway

            if not self.updateGenerateProgress():
                return False

        return True

    def generateCollection(self):
        collection = self.getCollection()
        index = self.getCollectionIndex()
        mods = self.getLeewayMods()
        leeways = set(filter(lambda x: x.spinners >= 1 and x.mode == 0, collection.beatmaps))

        if not self.calculateLeeways(leeways, mods):
            return

        for min, max in [(i*0.1, i*0.1+0.1) for i in range(20)][::-1]:
            name = f"{collection.name} " + self.config.leeways.format(min, max, mods)
            beatmaps = {beatmap for beatmap in leeways if min <= beatmap.leeway <= max}

            if len(beatmaps) >= 1:
                self.collectionDatabase.insert(index + 1, Collection(name, beatmaps))

        self.generateProgress.close()
        self.collectionTable.refresh()
