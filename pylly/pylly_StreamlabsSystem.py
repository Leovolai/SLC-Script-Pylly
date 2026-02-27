import json
import codecs
import os

import random
import time

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
    
    # Percentile conversion
    frequency_chance = Settings.Frequency / 100.0

    seed_value = hash(message + str(time.time())) % (2**32)
    random.seed(seed_value)

    if random.random() < frequency_chance:

        random_int = int(random.random() * 1000000)
        index_to_replace = random_int % len(words)

        Parent.Log(
            "DEBUG",
            "len(words) = {0}, random_int = {1}, Selected index: {2}".format(
                len(words), random_int, index_to_replace
            ),
        )

        words[index_to_replace] = Settings.ReplacementWord
        new_message = " ".join(words)

        Parent.SendStreamMessage(new_message)

        # Activate cooldown
        CooldownRemaining = Settings.CooldownMessages

def Tick():
    return