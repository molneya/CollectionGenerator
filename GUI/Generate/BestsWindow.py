
from Models.Score import Score
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox

class GenerateBestsWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Bests", requiresApi=True)

    def createForm(self, layout):
        self.createUsername(layout)
        self.createMode(layout)
        self.createSeparateMods(layout)
        self.createGenerateButton(layout)

    def generateCollection(self):
        if not self.getUsername():
            QMessageBox.critical(self, "Error", "Enter a username!")
            return
        try:
            user = self.ossapi.user(self.getUsername(), mode=self.getOssapiMode(), key="username")
            count = user.scores_best_count
        except:
            QMessageBox.critical(self, "Error", "Username doesn't exist!")
            return
        if not count:
            QMessageBox.critical(self, "Error", "This user has no plays to collect!")
            return

        # Main Loop
        self.createGenerateProgress(count)
        bests = []

        for offset in range((count - 1) // 50 + 1):
            for score in self.ossapi.user_scores(user.id, "best", mode=self.getOssapiMode(), limit=50, offset=50*offset):
                bests.append(Score.from_ossapi(score, self.collectionDatabase.database))

                if not self.updateGenerateProgress():
                    return

        # Make collections
        name = self.config.bests.format(user.username, self.getMode())
        beatmaps = {score.beatmap for score in bests}
        self.collectionDatabase.append(Collection(name, beatmaps))

        if self.getSeparateMods():
            include_visual = self.getIncludeVisual()
            unique_mods = set([score.get_mods(include_visual) for score in bests])

            for mod in unique_mods:
                modded_name = f"{name} " + self.config.modded.format(mod)
                beatmaps = {score.beatmap for score in bests if mod == score.get_mods(include_visual)}
                self.collectionDatabase.append(Collection(modded_name, beatmaps))

        self.generateProgress.close()
        self.collectionTable.refresh()
