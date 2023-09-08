
from GUI.Generate.BaseWindow import GenerateBaseWindow
from PyQt6.QtWidgets import QMessageBox
from io import BytesIO
import requests
import json

class GenerateFirstsCountryWindow(GenerateBaseWindow):
    def __init__(self, main):
        super().__init__(main, "Country Firsts")

    @classmethod
    def create(cls, main):
        if main.collectionDatabase.database.is_empty():
            QMessageBox.critical(main, "Error", "<p>Config error: osu!.db not loaded!</p><p>Please edit and reload your config before using this feature.</p>")
            return
        return cls(main)

    def createForm(self, layout):
        self.createUsername(layout)
        self.createGenerateButton(layout)

    def generateCollection(self):
        try:
            user = self.ossapi.user(self.getUsername(), key="username")
        except:
            QMessageBox.critical(self, "Error", "Username doesn't exist!")
            return

        headers = {
            'Content-type': "application/json",
            'Accept': "*/*",
        }
        parameters = {
            'file': None,
            'name': self.config.single.format(user.username, user.country_code.upper(), 1),
            'type': "create",
        }

        self.createGenerateProgress(1)

        # Request collection
        r = requests.post(f"https://api.huismetbenen.nl/player/{user.country_code.lower()}/{user.id}/collection", data=json.dumps(parameters), headers=headers)
        if not r.ok:
            QMessageBox.critical(self, "Error", "Request failed! Check snipe.huismetbenen.nl is up, otherwise their country may not be supported or they have no firsts.")
            return

        if not self.updateGenerateProgress():
            return

        bytestream = BytesIO(r.content)
        self.collectionDatabase.decode_collection_db(bytestream)

        self.generateProgress.close()
        self.collectionTable.refresh()
