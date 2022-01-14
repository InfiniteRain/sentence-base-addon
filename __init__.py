import requests
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning, askUser
import base64
import json
import time

from .SettingsDialog import Ui_SettingsDialog
from .globals import WEB_API_KEY, SIGN_IN_URI, QUERY_URI, REFRESH_URI


def openSettings() -> None:
    dialog = QDialog(mw)
    ui = Ui_SettingsDialog()
    ui.setupUi(dialog)
    dialog.show()


def validateSettings(config) -> bool:
    if config["refresh_token"] is None:
        showWarning("Not logged into Sentence Base. Please login from the settings.")
        return False

    note_type = mw.col.models.get(config["note_type"])

    if config["note_type"] is None or note_type is None:
        showWarning("Export note type is not setup. Please set it up in the settings.")
        return False

    if config["word_export"] is None and config["reading_export"] is None and config["sentence_export"] is None:
        showWarning("At least one export field should be setup. Please set it up in the settings.")
        return False

    fields = note_type["flds"]
    fields_len = len(fields)

    if (config["word_export"] is not None and config["word_export"] > fields_len - 1) \
        or (config["reading_export"] is not None and config["reading_export"] > fields_len - 1) \
            or (config["sentence_export"] is not None and config["sentence_export"] > fields_len - 1):
        showWarning("At least one export field is not setup correctly. Please set it up properly in the settings.")
        return False

    if config["deck"] is None:
        showWarning("Export deck is not setup. Please set it up in the settings.")
        return False

    return True


def ensureTokens(config) -> bool:
    current_timestamp = int(time.time())
    access_payload = json.loads(base64.b64decode(config["access_token"].split(".")[1] + "==").decode('ascii'))

    access_about_to_expire = current_timestamp + 300 > access_payload["exp"]

    if access_about_to_expire:
        body = {
            "grant_type": "refresh_token",
            "refresh_token": config["refresh_token"]
        }
        url = "%s?key=%s" % (REFRESH_URI, WEB_API_KEY)

        response = requests.post(url, data=body)
        response_json = response.json()

        if response.status_code != 200:
            showWarning("Token refresh failed.")
            return False

        config["access_token"] = response_json["id_token"]
        config["refresh_token"] = response_json["refresh_token"]
        mw.addonManager.writeConfig(__name__, config)

    return True


def addSentenceCards(config, batch_id, sentences):
    mw.col.models.setCurrent(mw.col.models.get(config["note_type"]))

    for sentence in sentences:
        new_note = mw.col.newNote()

        fields = new_note.fields
        field_map = [
            ('word_export', 'wordDictionaryForm'),
            ('reading_export', 'wordReading'),
            ('sentence_export', 'sentence')
        ]

        for entry in field_map:
            config_value = config[entry[0]]
            value_name = entry[1]

            if config_value is None:
                continue

            value = sentence["mapValue"]["fields"][value_name]["stringValue"]

            if fields[config_value] == "":
                fields[config_value] = value
                continue

            fields[config_value] += ("<br>%s" % value)

        mw.col.add_note(new_note, config["deck"])
        mw.reset()

    config["last_mined_batch"] = batch_id
    mw.addonManager.writeConfig(__name__, config)
    showInfo("Sentences from the most recent batch were successfully added.")


def importSentences():
    config = (mw.addonManager.getConfig(__name__) or {}).copy()

    if not validateSettings(config):
        return

    if not ensureTokens(config):
        return

    url = QUERY_URI
    headers = {"Authorization": "Bearer %s" % config["access_token"]}
    body = {
        "structuredQuery": {
            "from": {
                "collectionId": "batches"
            },
            "orderBy": [
                {
                    "field": {
                        "fieldPath": "createdAt"
                    },
                    "direction": "DESCENDING"
                }
            ],
            "limit": 1,
            "where": {
                "fieldFilter": {
                    "field": {
                        "fieldPath": "userUid"
                    },
                    "op": "EQUAL",
                    "value": {"stringValue": config["user_uid"]}
                }
            }
        }
    }

    response = requests.post(
        url, 
        headers=headers,
        json=body
    )
    response_json = response.json()

    if response.status_code != 200:
        showWarning("Failed to retrieve the most recent mining batch.")
        return

    if "document" not in response_json[0]:
        showWarning("No batch exists yet on your account.")
        return

    most_recent_batch_id = response_json[0]["document"]["name"].rsplit("/", 1)[-1]
    ask_text = "Sentences from the most recent batch appear to have already been added. Add the sentences anyway?"

    if config["last_mined_batch"] == most_recent_batch_id and not askUser(ask_text):
        return

    addSentenceCards(
        config, 
        most_recent_batch_id, 
        response_json[0]["document"]["fields"]["sentences"]["arrayValue"]
            ["values"]
    )


settings_action = QAction("Sentence Base Settings", mw)
qconnect(settings_action.triggered, openSettings)
mw.form.menuTools.addAction(settings_action)

import_action = QAction("Import Sentences", mw)
qconnect(import_action.triggered, importSentences)
mw.form.menuTools.addAction(import_action)
