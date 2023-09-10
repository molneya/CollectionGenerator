
from Models.Score import Score
from Models.Stream import StreamDecoder
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox
import os

class GenerateFilterScoresWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Filter Scores")
        self.scores = []

    @classmethod
    def create(cls, main):
        if main.collectionDatabase.database.is_empty():
            QMessageBox.critical(main, "Error", "<p>Config error: osu!.db not loaded!</p><p>Please edit and reload your config before using this feature.</p>")
            return
        return cls(main)

    def createForm(self, layout):
        self.createFilters(layout, Score)
        self.createGenerateButton(layout)

    def processDatabase(self, bytestream):
        bytestream.seek(4, 1)
        beatmap_count = StreamDecoder.int(bytestream)
        self.createGenerateProgress(beatmap_count)

        for _ in range(beatmap_count):
            StreamDecoder.ulebsstring(bytestream)
            score_count = StreamDecoder.int(bytestream)

            for _ in range(score_count):
                self.scores.append(Score.decode_database(bytestream, self.collectionDatabase.database))

            if not self.updateGenerateProgress():
                return False

        return True

    def generateCollection(self):
        if len(self.scores) == 0:
            filepath = os.path.join(self.config.directory, "scores.db")
            with open(filepath, 'rb') as db:
                if not self.processDatabase(db):
                    return

        scores = self.scores
        for key in self.getFilters(Score):
            scores = filter(key, scores)

        name = self.getFilterName()
        beatmaps = {score.beatmap for score in scores}
        self.collectionDatabase.append(Collection(name, beatmaps))

        self.generateProgress.close()
        self.collectionTable.refresh()
