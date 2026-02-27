import json
import codecs
import os

import random

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
        self.Frequency = 1

        if settingsfile:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                data = json.load(f)
                self.__dict__.update(data)

Settings = ScriptSettings()

CooldownRemaining = 0

def Init():
    if os.path.isfile(SettingsFile):
        Settings.__dict__.update(
            ScriptSettings(SettingsFile).__dict__
        )
    return

def ReloadSettings(jsonData):
    Parent.Log("DEBUG", "ReloadSettings CALLED")
    data = json.loads(jsonData)
    Settings.__dict__.update(data)
    
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

    # Probability check (use system RNG)
    if _sysrand.random() < float(Settings.Frequency):
        # uniformly pick an index from 0..len(words)-1 using SystemRandom
        index_to_replace = _sysrand.randrange(len(words))

        Parent.Log(
            "DEBUG",
            "Word amount = {0}, Selected index: {1}, Replacement chance: {2}".format(
                len(words), index_to_replace, Settings.Frequency
            ),
        )

        # Replace the word
        words[index_to_replace] = Settings.ReplacementWord
        new_message = " ".join(words)
        Parent.SendStreamMessage(new_message)

        # Activate cooldown
        CooldownRemaining = Settings.CooldownMessages

def Tick():
    return