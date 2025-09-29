# ==============================================================================
# speak.py
# ------------------------------------------------------------------------------
# This module is responsible for the Text-to-Speech (TTS) functionality of
# the assistant. It initializes the TTS engine and provides a simple function
# to convert a given text string into audible speech.
# ==============================================================================

import pyttsx3

def speak(audio):
    """
    Initializes the TTS engine, speaks the given text, and prints it to the console.

    This function is designed to be self-contained. It initializes the pyttsx3
    engine on each call to ensure statelessness and avoid potential engine
    conflicts, especially in a multi-threaded environment.

    Args:
        audio (str): The text string that the assistant should speak.
    """
    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()
    
    # Get the list of available voices
    voices = engine.getProperty('voices')
    
    # Print the assistant's response to the console for a visual log
    print(f"Assistant: {audio}")
    
    # Set the voice. voices[0] is typically male, voices[1] is female (can vary by system)
    # The current code has a hardcoded value of voices[2], which may not exist on all systems.
    # It's safer to check the length of the voices list first.
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id) # Defaulting to a female voice if available
    else:
        engine.setProperty('voice', voices[0].id) # Fallback to the first available voice
    
    # Queue the audio text to be spoken
    engine.say(audio)
    
    # Process the voice command queue and wait for it to complete
    engine.runAndWait()

