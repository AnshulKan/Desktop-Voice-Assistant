# ==============================================================================
# commands.py
# ------------------------------------------------------------------------------
# This module contains the core logic for all the voice assistant's commands.
# Each function corresponds to a specific user command and encapsulates the
# necessary logic to perform the action, such as making API calls, controlling
# the system, or managing user data like to-do lists.
# ==============================================================================

import re
import os
import time
import pyjokes
import spotipy
import smtplib
import requests
import datetime
import wikipedia
import pyautogui
import threading
import webbrowser
from speak import speak
from listen import listen
import shared_state
import screen_brightness_control as sbc
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from email.message import EmailMessage
from spotipy.oauth2 import SpotifyOAuth
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Import configuration variables from config.py
from config import (
    NEWS_API_KEY, WEATHER_API_KEY, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI, APP_PATHS, WEBSITE_URLS, TODO_FILE, EMAIL_ACCOUNTS, CONTACTS
)

# --- Helper Functions ---

def _get_spotify_client():
    """
    Authenticates with the Spotify API and returns a client object.
    Handles OAuth 2.0 flow for user authorization.

    Returns:
        spotipy.Spotify or None: An authenticated Spotify client object, or None if authentication fails.
        str or None: An error message if something goes wrong.
    """
    try:
        # Set up the authentication manager with credentials from the config file
        auth_manager = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="user-modify-playback-state user-read-playback-state"
        )
        # Create and return the Spotify client
        return spotipy.Spotify(auth_manager=auth_manager), None
    except Exception as e:
        print(f"Spotify Authentication Error: {e}")
        return None, "Could not connect to Spotify. Please check your credentials in config.py."

def _get_active_device(sp):
    """
    Finds the user's currently active Spotify device.

    Args:
        sp (spotipy.Spotify): An authenticated Spotify client object.

    Returns:
        str or None: The ID of the active device, or None if no active device is found.
        str or None: An error message if something goes wrong.
    """
    try:
        devices = sp.devices()
        # Check if the devices list exists and is not empty
        if devices and devices['devices']:
            return devices['devices'][0]['id'], None
        else:
            return None, "No active Spotify device found. Please start playing music on a device first."
    except Exception as e:
        print(f"Spotify Device Error: {e}")
        return None, "Could not find an active Spotify device."

def _read_todos():
    """Reads all tasks from the to-do list file."""
    if not os.path.exists(TODO_FILE):
        return []  # Return an empty list if the file doesn't exist
    with open(TODO_FILE, "r") as f:
        # Read all lines, strip whitespace, and filter out any empty lines
        return [line.strip() for line in f.readlines() if line.strip()]

def _write_todos(tasks):
    """Writes a list of tasks back to the to-do list file, overwriting the old content."""
    with open(TODO_FILE, "w") as f:
        for task in tasks:
            f.write(task + "\n")

# --- Command Functions ---

def get_greeting():
    """
    Returns a time-appropriate greeting.

    Returns:
        str: A greeting like "Good morning", "Good afternoon", or "Good evening".
    """
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning, Sir. How can I help you?"
    elif 12 <= hour < 18:
        return "Good afternoon, Sir. How can I help you?"
    else:
        return "Good evening, Sir. How can I help you?"

def add_todo(task):
    """
    Adds a new task to the to-do list.

    Args:
        task (str): The task to be added.

    Returns:
        str: A confirmation message.
    """
    if not task:
        return "I didn't hear a task to add."
    tasks = _read_todos()
    tasks.append(task)
    _write_todos(tasks)
    return f"Added '{task}' to your to-do list."

def show_todos():
    """
    Reads and returns the current to-do list.

    Returns:
        str: A spoken summary of the to-do list.
    """
    tasks = _read_todos()
    if not tasks:
        return "Your to-do list is empty."
    
    # Create a numbered list for the spoken response
    task_list_str = ". ".join(f"Task {i+1}: {t}" for i, t in enumerate(tasks))
    return f"Here is your to-do list: {task_list_str}"

def complete_todo(task_number_str):
    """
    Removes a task from the to-do list by its number.

    Args:
        task_number_str (str): The number of the task to complete.

    Returns:
        str: A confirmation or error message.
    """
    try:
        task_number = int(task_number_str)
        tasks = _read_todos()
        # Check if the task number is valid
        if 0 < task_number <= len(tasks):
            removed_task = tasks.pop(task_number - 1)
            _write_todos(tasks)
            return f"Completed and removed task: {removed_task}"
        else:
            return "That task number is not on your list."
    except (ValueError, TypeError):
        return "Sorry, I didn't understand the task number."
    except Exception as e:
        print(f"Error completing to-do: {e}")
        return "Sorry, something went wrong while updating your list."

def tell_time():
    """Returns the current time in a readable format."""
    return f"Sir, the time is {datetime.datetime.now().strftime('%I:%M %p')}"

def tell_date():
    """Returns the current date in a readable format."""
    return f"Today is {datetime.date.today().strftime('%B %d, %Y')}"

def tell_joke():
    """Returns a random joke."""
    return pyjokes.get_joke()

def search_wikipedia(query):
    """
    Searches Wikipedia for a given query and returns a summary.

    Args:
        query (str): The term to search for.

    Returns:
        str: A two-sentence summary or an error message.
    """
    try:
        # Get a 2-sentence summary of the Wikipedia page
        results = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {results}"
    except wikipedia.exceptions.PageError:
        return f"Sorry, I could not find any results for '{query}' on Wikipedia."
    except wikipedia.exceptions.DisambiguationError:
        return f"'{query}' could refer to multiple things. Please be more specific."

def get_weather(city="Bhopal"):
    """
    Fetches the current weather for a specified city using the OpenWeatherMap API.

    Args:
        city (str): The city for which to get the weather. Defaults to "Bhopal".

    Returns:
        str: The weather report or an error message.
    """
    if not WEATHER_API_KEY or "YOUR_" in WEATHER_API_KEY:
        return "Weather API key is not configured in config.py."
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        main = data["main"]
        weather = data["weather"][0]
        temperature = main["temp"]
        description = weather["description"]
        return f"The temperature in {city} is {temperature} degrees Celsius with {description}."
    except requests.exceptions.HTTPError:
        return f"Could not find weather data for {city}. Please check the city name."
    except requests.exceptions.RequestException:
        return "Could not connect to the weather service. Please check your internet connection."

def get_news():
    """
    Fetches the top 5 news headlines from India using the NewsAPI.

    Returns:
        str: A summary of the top headlines or an error message.
    """
    if not NEWS_API_KEY or "YOUR_" in NEWS_API_KEY:
        return "News API key is not configured in config.py."
    base_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            return "Sorry, I couldn't fetch the news right now."
        
        # Get the titles of the top 5 articles
        headlines = [article['title'] for article in articles[:5]]
        return "Here are the top news headlines: " + ". ".join(headlines)
    except requests.exceptions.RequestException:
        return "Could not connect to the news service."

def open_app(app_name):
    """
    Opens a desktop application based on a pre-configured path.

    Args:
        app_name (str): The name of the application to open.

    Returns:
        str: A confirmation or error message.
    """
    try:
        # Look up the application path in the config file (case-insensitive)
        path = APP_PATHS.get(app_name.lower())
        if not path:
            return f"Sorry, I don't have the path for {app_name}."
        
        # Check if the path exists before trying to open it
        if os.path.exists(path) or "microsoft.windows.camera" in path: # Special case for camera app
            os.startfile(path)
            return f"Opening {app_name}"
        else:
            return f"Sorry, the path for {app_name} seems to be invalid. Please check config.py."
    except Exception as e:
        print(f"Error in open_app: {e}")
        return f"Sorry, I encountered an error while trying to open {app_name}."
        
def open_website(website_name):
    """
    Opens a website based on a pre-configured URL.

    Args:
        website_name (str): The name of the website to open.

    Returns:
        str: A confirmation or error message.
    """
    try:
        # Look up the URL in the config file (case-insensitive)
        url = WEBSITE_URLS.get(website_name.lower())
        if not url:
            return f"Sorry, I don't have the URL for {website_name}."
        
        webbrowser.open(url)
        return f"Opening {website_name}."
    except Exception as e:
        print(f"Error opening website: {e}")
        return f"Sorry, an error occurred while trying to open {website_name}."

def search_web(query):
    """
    Performs a Google search for the given query.

    Args:
        query (str): The term to search for.

    Returns:
        str: A confirmation message.
    """
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching the web for {query}..."

def play_song(song_name):
    """
    Plays a specified song on Spotify.

    Args:
        song_name (str): The name of the song to play.

    Returns:
        str: A status message.
    """
    sp, error_msg = _get_spotify_client()
    if error_msg: return error_msg
    
    device_id, error_msg = _get_active_device(sp)
    if error_msg: return error_msg
    
    # Search for the track on Spotify
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(device_id=device_id, uris=[track_uri])
        return f"Playing {song_name} on Spotify..."
    else:
        return f"Sorry, I couldn't find the song '{song_name}' on Spotify."

def pause_music():
    """Pauses the currently playing music on Spotify."""
    sp, error_msg = _get_spotify_client()
    if error_msg: return error_msg
    device_id, error_msg = _get_active_device(sp)
    if error_msg: return error_msg
    
    sp.pause_playback(device_id=device_id)
    return "Pausing music."

def next_track():
    """Skips to the next track on Spotify."""
    sp, error_msg = _get_spotify_client()
    if error_msg: return error_msg
    device_id, error_msg = _get_active_device(sp)
    if error_msg: return error_msg
    
    sp.next_track(device_id=device_id)
    return "Playing next track."

def set_volume(level):
    """
    Sets the master system volume (Windows only).

    Args:
        level (int): The desired volume level (0-100).

    Returns:
        str: A confirmation or error message.
    """
    try:
        # Get the default audio endpoint (speakers)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # Set the volume level (scalar value from 0.0 to 1.0)
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level} percent."
    except Exception as e:
        print(f"Volume control error: {e}")
        return "I was unable to change the volume. This feature is for Windows only."

def set_brightness(level):
    """
    Sets the screen brightness.

    Args:
        level (int): The desired brightness level (0-100).

    Returns:
        str: A confirmation or error message.
    """
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level} percent."
    except Exception as e:
        print(f"Brightness control error: {e}")
        return "I was unable to change the brightness."

def take_screenshot():
    """Takes a screenshot and saves it with a timestamped filename."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot().save(filename)
        return f"Screenshot saved as {filename}"
    except Exception as e:
        print(f"Screenshot Error: {e}")
        return "Sorry, I couldn't take a screenshot."

def _timer_countdown(duration):
    """A helper function to run the timer countdown in a separate thread."""
    # Set the shared state flag to True so the main loop stops listening
    shared_state.is_background_task_running = True
    try:
        time.sleep(duration)
        # Speak directly since this is a background thread
        speak("Time's up!")
    finally:
        # Reset the flag when the timer is done
        shared_state.is_background_task_running = False

def set_timer(duration_str):
    """
    Sets a timer for a specified duration.

    Args:
        duration_str (str): The duration, e.g., "5 seconds" or "1 minute".

    Returns:
        str: A confirmation or error message.
    """
    try:
        # Use regex to find the number and the unit
        match = re.search(r'(\d+)\s+(second|seconds|minute|minutes)', duration_str)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            duration_seconds = 0
            if "minute" in unit:
                duration_seconds = value * 60
            elif "second" in unit:
                duration_seconds = value
            
            if duration_seconds > 0:
                # Run the countdown in a daemon thread so it doesn't block the main program
                thread = threading.Thread(target=_timer_countdown, args=(duration_seconds,), daemon=True)
                thread.start()
                return f"Timer set for {value} {unit}."
            
        return "Sorry, I didn't understand the timer duration. Please say it like 'set a timer for 5 seconds'."
    except Exception as e:
        print(f"Timer Error: {e}")
        return "Sorry, I couldn't set the timer."

def shutdown_computer():
    """Initiates computer shutdown after confirmation."""
    speak("Are you sure you want to shut down? Please say yes or no.")
    if (confirmation := listen()) and "yes" in confirmation:
        speak("Shutting down.")
        # os.system("shutdown /s /t 1") # Uncomment to enable shutdown
        return "Shutdown initiated by user."
    return "Shutdown cancelled."

def restart_computer():
    """Initiates computer restart after confirmation."""
    speak("Are you sure you want to restart? Please say yes or no.")
    if (confirmation := listen()) and "yes" in confirmation:
        speak("Restarting.")
        # os.system("shutdown /r /t 1") # Uncomment to enable restart
        return "Restart initiated by user."
    return "Restart cancelled."

def sleep_computer():
    """Puts the computer to sleep after confirmation."""
    speak("Are you sure you want to put the computer to sleep? Please say yes or no.")
    if (confirmation := listen()) and "yes" in confirmation:
        speak("Putting computer to sleep.")
        # os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0") # Uncomment for Windows
        return "Sleep mode initiated by user."
    return "Sleep command cancelled."

def calculate(query):
    """
    Performs a basic arithmetic calculation.

    Args:
        query (str): The calculation query, e.g., "5 times 3".

    Returns:
        str: The result or an error message.
    """
    # Replace spoken words with operators
    query = query.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("x", "*").replace("divided by", "/")
    try:
        # Use regex to find a simple calculation pattern (number operator number)
        match = re.search(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', query)
        if match:
            num1, operator, num2 = float(match.group(1)), match.group(2), float(match.group(3))
            
            if operator == '+': result = num1 + num2
            elif operator == '-': result = num1 - num2
            elif operator == '*': result = num1 * num2
            elif operator == '/':
                if num2 == 0: return "Error: Cannot divide by zero."
                result = num1 / num2
            
            # Return result as integer if it's a whole number, otherwise format to 2 decimal places
            return f"The result is {int(result) if result.is_integer() else f'{result:.2f}'}"
        else:
            return "I couldn't understand the calculation. Please say it like 'what is 5 times 3'."
    except Exception as e:
        print(f"Calculation Error: {e}")
        return "Sorry, I couldn't perform that calculation."

def send_email():
    """
    Guides the user through sending an email. This is an interactive command.
    It handles its own speaking and listening.

    Returns:
        str: A final status message (e.g., "Email sent" or "Email cancelled").
    """
    speak("Starting the email process.")
    
    try:
        # --- Get Sender Account ---
        speak("Which account would you like to send from?")
        sender_keyword = listen()
        if not sender_keyword or sender_keyword.lower() not in EMAIL_ACCOUNTS:
            return "Account not recognized. Email process cancelled."
        
        selected_account = EMAIL_ACCOUNTS[sender_keyword.lower()]
        EMAIL_ADDRESS, EMAIL_PASSWORD = selected_account["address"], selected_account["password"]
        
        # --- Get Recipient ---
        speak("Who is the recipient?")
        recipient_query = listen()
        recipient_email = CONTACTS.get(recipient_query.lower()) if recipient_query else None
        if not recipient_email:
            return "Recipient not found in contacts. Email process cancelled."
        
        # --- Get Subject ---
        subject = None
        while not subject:
            speak("What is the subject?")
            subject = listen()
            if not subject:
                speak("I didn't catch that. Please repeat the subject.")

        # --- Get Body ---
        body = None
        while not body:
            speak("What is the message?")
            body = listen()
            if not body:
                speak("I didn't catch that. Please repeat the message.")
        
        # --- Confirmation ---
        speak(f"Please confirm. You are sending an email to {recipient_query} with the subject '{subject}'. Is this correct? Say yes or no.")
        
        confirmation_attempts = 3
        while confirmation_attempts > 0:
            confirmation = listen()
            if confirmation and 'yes' in confirmation:
                # --- Send Email ---
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = recipient_email
                msg.set_content(body)
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)
                
                return "Email sent successfully."
            elif confirmation and 'no' in confirmation:
                return "Okay, email cancelled."
            else:
                confirmation_attempts -= 1
                if confirmation_attempts > 0:
                    speak("I didn't understand. Please say yes or no.")
        
        return "Confirmation failed after multiple attempts. Email cancelled."

    except Exception as e:
        print(f"Email Error: {e}")
        return "An error occurred during the email process. Email not sent."

