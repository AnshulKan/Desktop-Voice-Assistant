# ==============================================================================
# main.py
# ------------------------------------------------------------------------------
# This is the entry point and central control hub for the voice assistant.
# It contains the main application loop which continuously listens for user
# commands, parses them, calls the appropriate function from the commands
# module, and then speaks the response.
# ==============================================================================

import re
from speak import speak
from listen import listen
import commands as cmd
import shared_state
from logger import log_command, start_session

def main():
    """
    The main function that runs the voice assistant's core loop.
    """
    # Log the start of a new session
    start_session()
    speak("Initializing Assistant. How can I help you sir?")
    
    # The main loop that keeps the assistant running
    while True:
        # Check the shared state flag. If a background task (like a timer) is running,
        # the loop will skip listening for new commands until the task is complete.
        if shared_state.is_background_task_running:
            continue
            
        # Call the listen function to capture and transcribe user's speech
        query = listen()

        # If listen() returns None (e.g., timeout or couldn't understand),
        # skip this iteration and listen again.
        if not query:
            continue
        
        # Convert the query to lowercase for case-insensitive matching
        query_lower = query.lower()
        response = None
        status = "Command Handled" # Default status for logging

        # ======================================================================
        # Command Processing Block
        # ----------------------------------------------------------------------
        # This block uses a series of if/elif statements to match keywords in
        # the user's query and route them to the correct function in cmd.
        # ======================================================================
        
        if 'hello' in query_lower or 'hey' in query_lower:
            response = cmd.get_greeting()
        
        elif 'weather in' in query_lower:
            # Extract the city name from the query
            city = query_lower.split('in')[-1].strip()
            # Remove "the " if it's at the beginning (e.g., "the Bhopal")
            if city.startswith("the "):
                city = city.replace("the ", "", 1)
            
            if city:
                response = cmd.get_weather(city)
            else:
                response = "You need to specify a city for the weather."
                status = "Missing Information"
        
        elif 'news' in query_lower:
            response = cmd.get_news()
            
        elif 'wikipedia' in query_lower:
            # Extract the search term by removing the keyword "wikipedia"
            search_term = query_lower.replace("wikipedia", "").strip()
            response = cmd.search_wikipedia(search_term)

        elif 'search for' in query_lower:
            # Extract the search term by splitting the string at "for"
            search_term = query_lower.split("for")[-1].strip()
            response = cmd.search_web(search_term)
            
        elif 'add' in query_lower and ('task' in query_lower or 'list' in query_lower):
            # Use regex to find the task description
            task = re.search(r'add(.*?)(to my list|to my tasks|task)', query_lower)
            if task:
                response = cmd.add_todo(task.group(1).strip())
            else:
                response = "I didn't hear a task to add."
                status = "Missing Information"
        
        elif "show" in query_lower and ('list' in query_lower or 'tasks' in query_lower):
            response = cmd.show_todos()
        
        elif 'complete task' in query_lower:
            # Use regex to find the task number
            match = re.search(r'task (\d+)', query_lower)
            if match:
                response = cmd.complete_todo(match.group(1))
            else:
                response = "Please specify which task number to complete."
                status = "Missing Information"
        
        elif 'timer for' in query_lower:
            # Extract the duration string
            duration_str = query_lower.replace("timer for", "").strip()
            response = cmd.set_timer(duration_str)

        elif 'calculate' in query_lower:
            # Extract the calculation part of the query
            calc_query = query_lower.replace("calculate", "").strip()
            response = cmd.calculate(calc_query)

        elif 'time' in query_lower:
            response = cmd.tell_time()
        
        elif 'date' in query_lower:
            response = cmd.tell_date()

        elif 'joke' in query_lower:
            response = cmd.tell_joke()
            
        elif 'open website' in query_lower:
            website_name = query_lower.replace("open website", "").strip()
            response = cmd.open_website(website_name)
            
        # A more general 'open' command for applications
        elif 'open app' in query_lower or ('open' in query_lower and 'website' not in query_lower):
             app_name = query_lower.replace("open", "").strip()
             response = cmd.open_app(app_name)

        elif 'volume' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            if match and 0 <= int(match.group(1)) <= 100:
                response = cmd.set_volume(int(match.group(1)))
            else:
                response = "Please specify a volume level between 0 and 100."
                status = "Invalid Parameter"

        elif 'brightness' in query_lower:
            match = re.search(r'(\d+)', query_lower)
            if match and 0 <= int(match.group(1)) <= 100:
                response = cmd.set_brightness(int(match.group(1)))
            else:
                response = "Please specify a brightness level between 0 and 100."
                status = "Invalid Parameter"

        elif 'screenshot' in query_lower:
            response = cmd.take_screenshot()
        
        elif 'restart' in query_lower:
            response = cmd.restart_computer()
        
        elif 'sleep' in query_lower:
            response = cmd.sleep_computer()
        
        elif 'shutdown' in query_lower:
            response = cmd.shutdown_computer()

        elif 'email' in query_lower:
            # Email command is interactive and handles its own speaking/logging
            response = cmd.send_email()
            
        elif 'play music' in query_lower:
            song_name = query_lower.replace("play music", "").strip()
            response = cmd.play_song(song_name)
            
        elif 'pause music' in query_lower:
            response = cmd.pause_music()
            
        elif 'next track' in query_lower:
            response = cmd.next_track()
            
        elif 'goodbye' in query_lower or 'exit' in query_lower:
            response = "Goodbye Sir! Have a great day."
            speak(response)
            log_command(query, response, status)
            break # Exit the while loop to terminate the program
        
        else:
            # Default response if no keywords are matched
            response = "I am not sure how to respond to that."
            status = "Command Not Understood"
        
        # If a response was generated by any command, speak it and log the interaction
        if response:
            speak(response)
            log_command(query, response, status)

# This standard Python construct ensures that the main() function is called
# only when this script is executed directly (not when imported as a module).
if __name__ == "__main__":
    main()

