# -*- coding: utf-8 -*-
import json
import codecs
import os

import random
import string

# Use a SystemRandom instance so selections are based on OS entropy
# rather than the module state, which may be re-seeded by the chatbot
# environment each time the script is reloaded.
_sysrand = random.SystemRandom()

ScriptName = "Pylly"
Description = "Vaihtaa satunnaisen sanan 'pyllyksi'."
Creator = "Leovolai"
Version = "1.0.0"
Website = "https://twitch.tv/"

SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

class ScriptSettings(object):
    def __init__(self, settingsfile=None):
        self.ReplacementWord = "pylly"
        self.CooldownMessages = 10
        self.Frequency = 100

        if settingsfile:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                data = json.load(f)
                self.__dict__.update(data)

Settings = ScriptSettings()

CooldownRemaining = 0

def ReloadSettings(jsonData):
    Parent.Log("DEBUG", "ReloadSettings CALLED")
    data = json.loads(jsonData)
    Settings.__dict__.update(data)

def format_replacement(original, replacement):
    start_punct = ''
    end_punct = ''
    while original and original[0] in string.punctuation:
        start_punct += original[0]
        original = original[1:]
    while original and original[-1] in string.punctuation:
        end_punct = original[-1] + end_punct
        original = original[:-1]

    if original.isupper():
        replacement = replacement.upper()
    elif original.istitle():
        replacement = replacement.title()
    elif original.islower():
        replacement = replacement.lower()
    else:
        pass
    return start_punct + replacement + end_punct

# IGNORE LIST
IGNORE_WORDS = {
"ja", "sekä", "tai", "vai", "eli", "mutta", "vaan", "sillä", "että", "jotta", "koska", "jos", "ellei", "jollei", "mikäli", "kun",
"kunhan", "kunnes", "joskin", "vaikka"
}

# ==========
# SIJAMUODOT
# ==========

CASE_SUFFIXES = [
    "ssa", "ssä",   # inessiivi
    "sta", "stä",   # elatiivi
    "lla", "llä",   # adessiivi
    "lta", "ltä",   # ablatiivi
    "lle",          # allatiivi
    "ksi",          # translatiivi
    "tta", "ttä",   # abessiivi
    "na", "nä",     # essiivi
    "ta", "tä",     # partitiivi
    "n",            # genetiivi
]

def detect_suffix(word):
    lower = word.lower()
    for suffix in CASE_SUFFIXES:
        if lower.endswith(suffix):
            return suffix
    return ""


def inflect_replacement(original_word, replacement_base):
    # Strip punctuation for suffix detection
    core_word = original_word.strip(string.punctuation)

    suffix = detect_suffix(core_word)

    if suffix:
        replacement = replacement_base + suffix
    else:
        replacement = replacement_base

    return replacement

# =====================
# SIJAMUOTOILUJEN LOPPU
# =====================

def Init():
    if os.path.isfile(SettingsFile):
        Settings.__dict__.update(
            ScriptSettings(SettingsFile).__dict__
        )
    return
    
def Execute(data):
    global CooldownRemaining

    if not data.IsChatMessage():
        return

    bot_name = Parent.GetChannelName()
    if data.User == bot_name:
        return

    # If we're cooling down, decrement and exit
    if CooldownRemaining > 0:
        CooldownRemaining -= 1
        return

    message = data.Message
    
    words = [w.strip() for w in message.split() if w.strip()]

    if len(words) < 2:
        return

    if _sysrand.random() < float(Settings.Frequency) / 100:

        word_count = len(words)

        replacement_count = 1
        replace_threshold = 12

        if word_count > replace_threshold:
            replacement_count += (word_count // replace_threshold)

        # Build a list of candidate indices that are NOT in the ignore list
        candidate_indices = [
            i for i, w in enumerate(words)
            if w.lower().strip(string.punctuation) not in IGNORE_WORDS
        ]

        # If there are candidates, select indices to replace
        if candidate_indices:
            replacement_count = min(replacement_count, len(candidate_indices))
            indices_to_replace = _sysrand.sample(candidate_indices, replacement_count)

            for index in indices_to_replace:
                replacement = inflect_replacement(words[index], Settings.ReplacementWord)
                words[index] = format_replacement(words[index], replacement)

            new_message = " ".join(words)
            Parent.SendStreamMessage(new_message)

            CooldownRemaining = Settings.CooldownMessages

            Parent.Log(
                "DEBUG",
                "Word amount = {0}, Replacement count = {1}, Indices: {2}, Replacement chance: {3}".format(
                    word_count, replacement_count, indices_to_replace, Settings.Frequency
                ),
            )

def Tick():
    return