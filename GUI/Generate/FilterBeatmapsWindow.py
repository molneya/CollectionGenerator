
from Models.Beatmap import Beatmap
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow

class GenerateFilterBeatmapsWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Filter Beatmaps", requiresDatabase=True)

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
