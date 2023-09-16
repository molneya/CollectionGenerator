
from Models.Score import Score
from Models.Collection import Collection
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox

class GenerateFirstsGlobalWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Global Firsts", requiresApi=True)

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
            count = user.scores_first_count
        except:
            QMessageBox.critical(self, "Error", "Username doesn't exist!")
            return
        if not count:
            QMessageBox.critical(self, "Error", "This user has no plays to collect!")
            return

        # Main Loop
        self.createGenerateProgress(count)
        firsts = []

        for offset in range((count - 1) // 50 + 1):
            for score in self.ossapi.user_scores(user.id, "firsts", mode=self.getOssapiMode(), limit=50, offset=50*offset):
                firsts.append(Score.from_ossapi(score, self.collectionDatabase.database))

                if not self.updateGenerateProgress():
                    return

        # Make collections
        name = self.config.single.format(user.username, self.getMode(), 1)
        beatmaps = {score.beatmap for score in firsts}
        self.collectionDatabase.append(Collection(name, beatmaps))

        if self.getSeparateMods():
            include_visual = self.getIncludeVisual()
            unique_mods = {score.get_mods(include_visual) for score in firsts}

            for mod in unique_mods:
                modded_name = f"{name} " + self.config.modded.format(mod)
                beatmaps = {score.beatmap for score in firsts if mod == score.get_mods(include_visual)}
                self.collectionDatabase.append(Collection(modded_name, beatmaps))

        self.generateProgress.close()
        self.collectionTable.refresh()
