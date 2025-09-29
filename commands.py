import datetime
import wikipedia
import webbrowser
import os
import requests
import pyjokes
import pyautogui
import time
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import threading
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import screen_brightness_control as sbc
from speak import speak
from listen import listen
from config import (NEWS_API_KEY, WEATHER_API_KEY, APP_PATHS, WEBSITE_URLS, 
                    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, 
                    TODO_FILE, EMAIL_ACCOUNTS, CONTACTS)
import shared_state
import smtplib
from email.message import EmailMessage
import re

# --- Helper Functions ---

def _get_spotify_client_and_device():
    try:
        auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope="user-modify-playback-state user-read-playback-state")
        sp = spotipy.Spotify(auth_manager=auth_manager)
        devices = sp.devices()
        if not devices or not devices['devices']:
            return "No active Spotify device found. Please start playing music on a device first.", None, None
        return None, sp, devices['devices'][0]['id']
    except Exception as e:
        print(f"Spotify Connection Error: {e}")
        return "Could not connect to Spotify. Please check your credentials in the config file.", None, None

def _read_todos():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def _write_todos(tasks):
    with open(TODO_FILE, "w") as f:
        for task in tasks:
            f.write(task + "\n")
            
# --- Command Functions (now returning strings) ---

def handle_greeting(query):
    if 'how are you' in query or 'how r u' in query:
        return "I am doing great, thank you for asking!"
    else:
        return "Hello Sir, how may I help you?"

def add_todo(task):
    if not task:
        return "I didn't hear a task to add."
    tasks = _read_todos()
    tasks.append(task)
    _write_todos(tasks)
    return f"Okay, I've added '{task}' to your list."

def show_todos():
    tasks = _read_todos()
    if not tasks:
        return "Your to-do list is empty."
    else:
        task_list_str = "\n".join([f"{i}. {task}" for i, task in enumerate(tasks, 1)])
        print("\n--- Your To-Do List ---\n" + task_list_str + "\n------------------------")
        return "Displaying your to-do list in the console."

def complete_todo(task_number_str):
    try:
        task_number = int(task_number_str)
        tasks = _read_todos()
        if 0 < task_number <= len(tasks):
            removed_task = tasks.pop(task_number - 1)
            _write_todos(tasks)
            return f"Completed: {removed_task}"
        else:
            return "That task number is not on your list."
    except (ValueError, IndexError):
        return "Sorry, I didn't understand the task number."

def tell_time():
    return "Sir, the time is " + datetime.datetime.now().strftime("%H:%M:%S")

def tell_date():
    return "Today is " + datetime.date.today().strftime('%B %d, %Y')

def tell_joke():
    return pyjokes.get_joke()

def search_wikipedia(query):
    try:
        return "According to Wikipedia: " + wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.PageError:
        return f"Sorry, I could not find any results for {query} on Wikipedia."
    except wikipedia.exceptions.DisambiguationError:
        return f"{query} is a disambiguation page. Please be more specific."

def get_weather(city="Delhi"):
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        return "Weather API key not configured."
    base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        if data["cod"] != "404":
            main, weather = data["main"], data["weather"][0]
            return f"The temperature in {city} is {main['temp']}°C with {weather['description']}."
        else:
            return "City not found."
    except requests.RequestException as e:
        print(f"Weather API Error: {e}")
        return "Sorry, I couldn't fetch the weather right now."


def open_app(app_name):
    path = APP_PATHS.get(app_name.lower())
    if not path:
        return f"Sorry, I don't have the path for {app_name}."
    try:
        os.startfile(path)
        return f"Opening {app_name}."
    except Exception as e:
        print(f"Error opening app '{app_name}': {e}")
        return f"Sorry, I failed to open {app_name}."

def open_website(url_key):
    url = WEBSITE_URLS.get(url_key.lower())
    if not url:
        return f"I don't have the URL for {url_key} in my configuration."
    webbrowser.open(f"https://{url}")
    return f"Opening {url_key}."

def get_news():
    if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        return "News API key is not configured."
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        if news_data.get("status") == "ok":
            articles = news_data.get("articles", [])
            if articles:
                headlines = "\n".join([f"Headline {i+1}: {a['title']}" for i, a in enumerate(articles[:3])])
                speak("Here are the top news headlines:") # Speaks first
                return headlines # Returns for logging
            return "I couldn't find any top headlines at the moment."
        return "Sorry, I couldn't fetch the news. The API reported an error."
    except requests.RequestException as e:
        print(f"News API Error: {e}")
        return "Sorry, something went wrong while fetching the news."

def take_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    pyautogui.screenshot(filename)
    return f"Screenshot saved as {filename}"

# Timer countdown
def _timer_countdown(duration):
    shared_state.is_background_task_running = True
    try:
        if duration > 10:
            time.sleep(duration - 10)
        countdown_start = min(duration, 10)
        for i in range(countdown_start, 0, -1):
            speak(str(i))
            time.sleep(1)
        speak("Time's up!")
    finally:
        shared_state.is_background_task_running = False

# Set timer
def set_timer(duration_str):
    try:
        parts = duration_str.split()
        duration = 0
        if "minute" in duration_str:
            duration = int(parts[0]) * 60
        elif "second" in duration_str:
            duration = int(parts[0])
        if duration > 0:
            thread = threading.Thread(target=_timer_countdown, args=(duration,), daemon=True)
            thread.start()
            return f"Timer set for {duration_str}."
        else:
            speak("Sorry, I didn't understand the duration.")
            return "Sorry, I didn't understand the duration."
    except Exception as e:
        speak("Sorry, I couldn't set the timer.")
        print(f"Timer Error: {e}")
        return "Sorry, a general error occurred while setting the timer."

def search_web(query):
    if not query:
        return "What would you like me to search for?"
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching the web for {query}..."

def play_song(song_name):
    error, sp, device_id = _get_spotify_client_and_device()
    if error: return error
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        sp.start_playback(device_id=device_id, uris=[track['uri']])
        return f"Playing {track['name']} on Spotify."
    return f"Sorry, I couldn't find the song {song_name} on Spotify."

def pause_music():
    error, sp, device_id = _get_spotify_client_and_device()
    if error: return error
    sp.pause_playback(device_id=device_id)
    return "Pausing music."

def resume_music():
    error, sp, device_id = _get_spotify_client_and_device()
    if error: return error
    sp.start_playback(device_id=device_id)
    return "Resuming music."

def next_track():
    error, sp, device_id = _get_spotify_client_and_device()
    if error: return error
    sp.next_track(device_id=device_id)
    return "Playing next track."

def set_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level} percent."
    except Exception as e:
        print(f"Volume control error: {e}")
        return "I was unable to change the volume."

def set_brightness(level):
    try:
        sbc.set_brightness(level)
        return f"Brightness set to {level} percent."
    except Exception as e:
        print(f"Brightness control error: {e}")
        return "I was unable to change the brightness."

def shutdown_computer():
    speak("Are you sure you want to shut down? Say yes to confirm.")
    if (confirmation := listen()) and "yes" in confirmation.lower():
        os.system("shutdown /s /t 1")
        return "Shutting down the computer."
    return "Shutdown cancelled."

def restart_computer():
    speak("Are you sure you want to restart? Say yes to confirm.")
    if (confirmation := listen()) and "yes" in confirmation.lower():
        os.system("shutdown /r /t 1")
        return "Restarting the computer."
    return "Restart cancelled."

def sleep_computer():
    speak("Are you sure you want to sleep? Say yes to confirm.")
    if (confirmation := listen()) and "yes" in confirmation.lower():
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting the computer to sleep."
    return "Sleep command cancelled."

def calculate(query):
    expression = query.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("x", "*").replace("divided by", "/").replace("what is", "").strip()
    try:
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        print(f"Calculation Error: {e}")
        return "Sorry, I couldn't perform that calculation."

def send_email():
    """Guides the user through sending an email with a visual confirmation."""
    speak("Starting the email process.")
    
    # 1. Select Sender Account
    sender_keyword, attempts_left = None, 3
    account_names = " or ".join(EMAIL_ACCOUNTS.keys())
    while attempts_left > 0:
        speak(f"Which email account to send from? You can say {account_names}.")
        keyword_input = listen()
        if keyword_input and keyword_input in EMAIL_ACCOUNTS:
            sender_keyword = keyword_input
            break
        attempts_left -= 1
        if attempts_left > 0:
            speak(f"I don't recognize that account. {attempts_left} attempts left.")
    
    if not sender_keyword:
        return "Maximum attempts reached. Email process aborted."

    selected_account = EMAIL_ACCOUNTS[sender_keyword]
    email_address, email_password = selected_account["address"], selected_account["password"]
    
    if "YOUR_" in email_address or "YOUR_" in email_password:
        return f"Credentials for '{sender_keyword}' are not configured."

    # 2. Get Recipient
    speak("Who is the recipient? Say a name, or 'cancel'.")
    recipient_email = None
    while not recipient_email:
        query = listen()
        if not query:
            speak("Didn't catch that. Please repeat the recipient.")
            continue
        
        query_lower = query.lower()
        if 'cancel' in query_lower:
            return "Email composition cancelled by user."
        if query_lower in CONTACTS:
            recipient_email = CONTACTS[query_lower]
            break
        
        speak(f"'{query}' is not a valid contact. Please try again.")

    # 3. Get Subject
    subject = None
    while not subject:
        speak("What is the subject?")
        subject_input = listen()
        if subject_input:
            subject = subject_input
            break
        speak("I didn't catch that. Please repeat the subject.")

    # 4. Get Body
    body = None
    while not body:
        speak("What is the message?")
        body_input = listen()
        if body_input:
            body = body_input
            break
        speak("I didn't catch that. Please repeat the message.")
    
    # 5. Visual Confirmation
    print("\n" + "="*25)
    print("      EMAIL PREVIEW")
    print("="*25)
    print(f"From:    {email_address}")
    print(f"To:      {recipient_email}")
    print(f"Subject: {subject}")
    print("-"*25)
    print(f"Body:\n{body}")
    print("="*25 + "\n")
    
    speak("Creating email. The details are displayed. Is this correct? Please say yes or no.")
    
    # 6. Final Confirmation (Yes/No)
    for _ in range(3): # Give 3 attempts for confirmation
        confirmation = listen()
        if confirmation:
            if 'yes' in confirmation:
                try:
                    speak("Sending the email now.")
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = email_address
                    msg['To'] = recipient_email
                    msg.set_content(body)
                    
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(email_address, email_password)
                        smtp.send_message(msg)
                    
                    return "Email sent successfully."

                except Exception as e:
                    print(f"Email Sending Error: {e}")
                    speak("Sorry, a critical error occurred while sending the email.")
                    return "An error occurred. Email not sent."
            
            elif 'no' in confirmation:
                speak("Email cancelled.")
                return "Email cancelled by user."

        speak("I didn't understand. Please say 'yes' to send or 'no' to cancel.")
        
    speak("Email cancelled.")
    return "Email cancelled. No confirmation received."

