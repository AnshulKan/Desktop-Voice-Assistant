import pyttsx3
def speak(audio):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"Assistant: {audio}")
    engine.setProperty('voice', voices[2].id)
    engine.say(audio)
    engine.runAndWait()

