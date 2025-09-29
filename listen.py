import speech_recognition as sr

def listen():
    """Listens for user input and adjusts for ambient noise for better accuracy."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # Adjust for ambient noise to improve recognition accuracy
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 1

        try:
            audio = r.listen(source)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("Recognizer could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in listen(): {e}")
        return None

