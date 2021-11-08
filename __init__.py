from aqt import mw
from aqt.qt import *
from .SettingsDialog import Ui_SettingsDialog


API_URI = 'https://infiniterain.io'


def testFunction() -> None:
    dialog = QDialog(mw)
    ui = Ui_SettingsDialog()
    ui.setupUi(dialog)
    dialog.show()

    # mw.col.models.all_names_and_ids()
    # mw.col.decks.all_names_and_ids()

    # mw.col.models.setCurrent(mw.col.models.get(1636319071551))
    # new_note = mw.col.newNote()
    # new_note.fields = ["hello", "wprld"]
    # mw.col.add_note(new_note, mw.col.decks.all_names_and_ids()[1].id)
    # mw.reset()


action = QAction("test", mw)
qconnect(action.triggered, testFunction)
mw.form.menuTools.addAction(action)
