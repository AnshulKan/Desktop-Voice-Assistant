# ==============================================================================
# CONFIGURATION FILE FOR DESKTOP VOICE ASSISTANT
# ==============================================================================
# Instructions:
# 1. Fill in all the placeholder values (e.g., "YOUR_API_KEY").
# 2. For email, generate an "App Password" from your Google Account settings.
#    DO NOT use your regular email password here for security reasons.
# 3. Save the file after filling in your details.
# ==============================================================================

# --- API Keys ---
# Get your keys from:
# News API: https://newsapi.org/
# OpenWeatherMap API: https://openweathermap.org/api
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"

# --- Spotify Credentials ---
# Get your credentials from the Spotify Developer Dashboard:
# https://developer.spotify.com/dashboard/
SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback/'

# --- Application Paths (Examples for Windows) ---
# Update these paths to match the locations on your computer.
# Use double backslashes (\\) for Windows paths.
APP_PATHS = {
    "notepad": "C:\\Windows\\System32\\notepad.exe",
    "vs code": "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "browser": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "calculator": "C:\\Windows\\System32\\calc.exe"
}

# --- Website URLs ---
WEBSITE_URLS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "linkedin": "https://www.linkedin.com",
    "github": "https://www.github.com"
}

# --- To-Do List File ---
TODO_FILE = "todo.txt"

# --- Email Configuration ---
EMAIL_ACCOUNTS = {
    "personal": {
        "address": "your_email@gmail.com",
        "password": "YOUR_GMAIL_APP_PASSWORD" # Use an App Password, not your regular password
    },
    # You can add more accounts if needed
    # "work": {
    # "address": "your_work_email@example.com",
    # "password": "YOUR_WORK_APP_PASSWORD"
    # }
}

# --- Email Contacts ---
# Add names and email addresses for quick access
CONTACTS = {
    "test contact": "recipient_email@example.com",
    "team lead": "lead_email@example.com",
    "friend": "friend_email@example.com"
}
