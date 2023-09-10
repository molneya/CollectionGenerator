
from Models.Score import Score
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox
import requests
import json

class GenerateLeaderboardsWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Leaderboards")

    @classmethod
    def create(cls, main):
        if main.collectionDatabase.database.is_empty():
            QMessageBox.critical(main, "Error", "<p>Config error: osu!.db not loaded!</p><p>Please edit and reload your config before using this feature.</p>")
            return
        return cls(main)

    def createForm(self, layout):
        self.createUsername(layout)
        self.createMode(layout)
        self.createRanks(layout)
        self.createSeparateMods(layout)
        self.createGenerateButton(layout)

    def generateCollection(self):
        if not self.getUsername():
            QMessageBox.critical(self, "Error", "Enter a username!")
            return

        headers = {
            'Content-type': "application/json",
            'Accept': "text/plain",
        }
        parameters = {
            'page': 1,
            'u1': self.getUsername(),
            'rankMin': self.getRankMin(),
            'rankMax': self.getRankMax(),
            'gamemode': self.getIntMode(),
            'sortOrder': 0,
            'sortBy': 0,
            'resultType': 2,
        }

        # First request
        r = requests.post("https://osustats.ppy.sh/api/getScores", data=json.dumps(parameters), headers=headers)
        if not r.ok:
            QMessageBox.critical(self, "Error", "Request failed! Check osustats.ppy.sh is up, otherwise the username probably doesn't exist.")
            return

        scores, count, still_scores, _ = r.json()
        if not count:
            QMessageBox.critical(self, "Error", "This user has no plays to collect!")
            return

        self.createGenerateProgress(count)
        leaderboards = []

        # First request loop
        for score in scores:
            leaderboards.append(Score.from_osustats(score, self.collectionDatabase.database))
            if not self.updateGenerateProgress():
                return

        # Main Loop
        while still_scores:
            self.wait(2000) # No built in rate limit here. Err towards the safer side of things.
            parameters['page'] += 1

            r = requests.post("https://osustats.ppy.sh/api/getScores", data=json.dumps(parameters), headers=headers)
            if not r.ok:
                QMessageBox.critical(self, "Error", "Request failed! Check osustats.ppy.sh is up, otherwise something has gone terribly wrong.")
                return

            scores, count, still_scores, _ = r.json()

            for score in scores:
                leaderboards.append(Score.from_osustats(score, self.collectionDatabase.database))
                if not self.updateGenerateProgress():
                    return

        # Make collections
        if self.getRankMin() == self.getRankMax(): name = self.config.single.format(self.getUsername(), self.getMode(), self.getRankMin())
        else: name = self.config.range.format(self.getUsername(), self.getMode(), self.getRankMin(), self.getRankMax())
        beatmaps = {score.beatmap for score in leaderboards}
        self.collectionDatabase.append(Collection(name, beatmaps))

        if self.getSeparateMods():
            include_visual = self.getIncludeVisual()
            unique_mods = {score.get_mods(include_visual) for score in leaderboards}

            for mod in unique_mods:
                modded_name = f"{name} " + self.config.modded.format(mod)
                beatmaps = {score.beatmap for score in leaderboards if mod == score.get_mods(include_visual)}
                self.collectionDatabase.append(Collection(modded_name, beatmaps))

        self.generateProgress.close()
        self.collectionTable.refresh()
