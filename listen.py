# ==============================================================================
# listen.py
# ------------------------------------------------------------------------------
# This module handles all speech recognition tasks for the assistant.
# It uses the SpeechRecognition library to capture audio from the microphone
# and transcribe it into text using an online API (Google Web Speech).
# ==============================================================================

import speech_recognition as sr

def listen():
    """
    Listens for a command from the user via microphone and transcribes it to text.

    This function actively listens for a single utterance, adjusts for ambient noise
    to improve accuracy, and uses Google's Web Speech API for transcription.

    Returns:
        str or None: The transcribed text in lowercase if successful, otherwise None.
    """
    # Initialize the recognizer
    r = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")
        
        # Set a pause threshold to determine the end of a phrase
        r.pause_threshold = 1
        
        # Calibrate the recognizer to the ambient noise level for better accuracy
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Listen for the user's input. The timeout and phrase_time_limit
            # prevent the recognizer from waiting indefinitely.
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
            return None

    # --- Try to recognize the speech using Google's online service ---
    try:
        print("Recognizing...")
        # Use Google's API to transcribe the audio to text
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        # Return the transcribed text in lowercase
        return query.lower()
    
    # Handle cases where the API could not understand the audio
    except sr.UnknownValueError:
        print("Recognizer could not understand the audio.")
        return None
        
    # Handle cases where the API is unreachable or returns an error
    except sr.RequestError as e:
        print(f"Could not request results from the speech recognition service; {e}")
        return None
        
    # Handle any other unexpected errors
    except Exception as e:
        print(f"An unexpected error occurred during speech recognition: {e}")
        return None

