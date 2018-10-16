import pyttsx3 as pyttsx

slowdown_rate = 0
fastup_rate = 10

lyrics = open("neural_rap_1.txt", 'r', encoding='utf-8').read().split("\n")


def lyric(name):
    print(name)


engine = pyttsx.init()
engine.connect('started-utterance', lyric)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - slowdown_rate + fastup_rate)

for line in lyrics:
    engine.say(line, name=line)
engine.runAndWait()
