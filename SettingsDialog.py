from PyQt5 import QtCore, QtGui, QtWidgets
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
import urllib.request
import json
from . import API_URI

class Ui_SettingsDialog(object):
    def __init__(self):
        self.current_config = (mw.addonManager.getConfig(__name__) or {}).copy()

    def populateComboBoxes(self):
        self.combo_box_note_type.addItem("None", {"id": None})
        models = mw.col.models.all_names_and_ids()
        for index, model in enumerate(models):
            self.combo_box_note_type.addItem(model.name, {"id": model.id})
            if self.current_config["note_type"] == model.id:
                self.combo_box_note_type.setCurrentIndex(index + 1)
        qconnect(
            self.combo_box_note_type.currentIndexChanged,
            lambda: self.onNoteChanged(),
        )

        self.combo_box_deck.addItem("None", {"id": None})
        decks = mw.col.decks.all_names_and_ids()
        for index, deck in enumerate(decks):
            self.combo_box_deck.addItem(deck.name, {"id": deck.id})
            if self.current_config["deck"] == deck.id:
                self.combo_box_deck.setCurrentIndex(index + 1)

        self.onNoteChanged()

    def onNoteChanged(self):
        note_type_id = self.combo_box_note_type.currentData()["id"]
        combo_entries = [
            (self.combo_box_word, "word_export"),
            (self.combo_box_reading, "reading_export"),
            (self.combo_box_sentence, "sentence_export")
        ]

        for combo_entry in combo_entries:
            combo_box = combo_entry[0]
            combo_config_key = combo_entry[1]

            combo_box.clear()
            combo_box.addItem("None", {"id": None})

            if note_type_id is None:
                combo_box.setEnabled(False)
                continue

            combo_box.setEnabled(True)
            for index, field in enumerate(mw.col.models.get(note_type_id)["flds"]):
                combo_box.addItem(field["name"], {"id": field["ord"]})
                if field["ord"] == self.current_config[combo_config_key]:
                    combo_box.setCurrentIndex(index + 1)


    def onAccept(self, SettingsDialog):
        self.current_config["note_type"] = self.combo_box_note_type.currentData()["id"]
        self.current_config["word_export"] = self.combo_box_word.currentData()["id"]
        self.current_config["reading_export"] = self.combo_box_reading.currentData()["id"]
        self.current_config["sentence_export"] = self.combo_box_sentence.currentData()["id"]
        self.current_config["deck"] = self.combo_box_deck.currentData()["id"]

        mw.addonManager.writeConfig(__name__, self.current_config)
        SettingsDialog.close()


    def onLogin(self):
        body = {
            "email": self.line_edit_email.text(),
            "password": self.line_edit_password.text()
        }
        # url =


    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(302, 372)
        SettingsDialog.setModal(True)
        self.button_box_action = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.button_box_action.setGeometry(QtCore.QRect(140, 330, 141, 32))
        self.button_box_action.setOrientation(QtCore.Qt.Horizontal)
        self.button_box_action.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box_action.setObjectName("button_box_action")
        self.label_email = QtWidgets.QLabel(SettingsDialog)
        self.label_email.setGeometry(QtCore.QRect(20, 20, 111, 16))
        self.label_email.setObjectName("label_email")
        self.line_separator = QtWidgets.QFrame(SettingsDialog)
        self.line_separator.setGeometry(QtCore.QRect(20, 110, 261, 20))
        self.line_separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_separator.setObjectName("line_separator")
        self.label_password = QtWidgets.QLabel(SettingsDialog)
        self.label_password.setGeometry(QtCore.QRect(20, 50, 71, 16))
        self.label_password.setObjectName("label_password")
        self.line_edit_email = QtWidgets.QLineEdit(SettingsDialog)
        self.line_edit_email.setGeometry(QtCore.QRect(140, 20, 141, 21))
        self.line_edit_email.setObjectName("line_edit_email")
        self.line_edit_password = QtWidgets.QLineEdit(SettingsDialog)
        self.line_edit_password.setGeometry(QtCore.QRect(140, 50, 141, 21))
        self.line_edit_password.setObjectName("line_edit_password")
        self.button_login = QtWidgets.QPushButton(SettingsDialog)
        self.button_login.setGeometry(QtCore.QRect(20, 80, 261, 32))
        self.button_login.setObjectName("button_login")
        qconnect(
            self.button_login.pressed,
            lambda: self.onLogin()
        )

        self.combo_box_note_type = QtWidgets.QComboBox(SettingsDialog)
        self.combo_box_note_type.setGeometry(QtCore.QRect(130, 130, 161, 32))
        self.combo_box_note_type.setObjectName("combo_box_note_type")

        self.combo_box_word = QtWidgets.QComboBox(SettingsDialog)
        self.combo_box_word.setGeometry(QtCore.QRect(130, 170, 161, 32))
        self.combo_box_word.setObjectName("combo_box_word")

        self.combo_box_reading = QtWidgets.QComboBox(SettingsDialog)
        self.combo_box_reading.setGeometry(QtCore.QRect(130, 210, 161, 32))
        self.combo_box_reading.setObjectName("combo_box_reading")

        self.combo_box_sentence = QtWidgets.QComboBox(SettingsDialog)
        self.combo_box_sentence.setGeometry(QtCore.QRect(130, 250, 161, 32))
        self.combo_box_sentence.setObjectName("combo_box_sentence")

        self.combo_box_deck = QtWidgets.QComboBox(SettingsDialog)
        self.combo_box_deck.setGeometry(QtCore.QRect(130, 290, 161, 32))
        self.combo_box_deck.setObjectName("combo_box_deck")

        self.label_note_type = QtWidgets.QLabel(SettingsDialog)
        self.label_note_type.setGeometry(QtCore.QRect(20, 130, 111, 31))
        self.label_note_type.setObjectName("label_note_type")
        self.label_word_export = QtWidgets.QLabel(SettingsDialog)
        self.label_word_export.setGeometry(QtCore.QRect(20, 170, 111, 31))
        self.label_word_export.setObjectName("label_word_export")
        self.label_reading_export = QtWidgets.QLabel(SettingsDialog)
        self.label_reading_export.setGeometry(QtCore.QRect(20, 210, 111, 31))
        self.label_reading_export.setObjectName("label_reading_export")
        self.label_sentence_export = QtWidgets.QLabel(SettingsDialog)
        self.label_sentence_export.setGeometry(QtCore.QRect(20, 250, 111, 31))
        self.label_sentence_export.setObjectName("label_sentence_export")
        self.label_deck = QtWidgets.QLabel(SettingsDialog)
        self.label_deck.setGeometry(QtCore.QRect(20, 290, 111, 31))
        self.label_deck.setObjectName("label_deck")

        self.retranslateUi(SettingsDialog)
        qconnect(self.button_box_action.accepted, lambda: self.onAccept(SettingsDialog))
        self.button_box_action.rejected.connect(SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

        self.populateComboBoxes()

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Dialog"))
        self.label_email.setText(_translate("SettingsDialog", "Email:"))
        self.label_password.setText(_translate("SettingsDialog", "Password:"))
        self.button_login.setText(_translate("SettingsDialog", "Login"))
        self.label_note_type.setText(_translate("SettingsDialog", "Note Type:"))
        self.label_word_export.setText(_translate("SettingsDialog", "Word Export:"))
        self.label_reading_export.setText(_translate("SettingsDialog", "Reading Export:"))
        self.label_sentence_export.setText(_translate("SettingsDialog", "Sentence Export:"))
        self.label_deck.setText(_translate("SettingsDialog", "Deck:"))
