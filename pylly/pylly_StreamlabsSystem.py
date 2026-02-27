import random
import time

ScriptName = "Pylly"
Description = "Vaihtaa satunnaisen sanan 'pyllyksi'."
Creator = "Leovolai"
Version = "1.0.0"
Website = "https://twitch.tv/"

configFile = "config.json"
settings = {}

Frequency = 0.1
ReplacementWord = "pylly"

CooldownMessages = 10
CooldownRemaining = 0

def Init():
    return

def Execute(data):
    global Frequency
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

    seed_value = hash(message + str(time.time())) % (2**32)
    random.seed(seed_value)

    if random.random() < Frequency:

        random_int = int(random.random() * 1000000)
        index_to_replace = random_int % len(words)

        Parent.Log(
            "DEBUG",
            "len(words) = {0}, random_int = {1}, Selected index: {2}".format(
                len(words), random_int, index_to_replace
            ),
        )

        words[index_to_replace] = ReplacementWord
        new_message = " ".join(words)
        Parent.SendStreamMessage(new_message)

        # Activate cooldown
        CooldownRemaining = CooldownMessages

def Tick():
    return