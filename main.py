import re
import sys
import commands as cmd
from listen import listen
from speak import speak
from logger import start_session, log_command
import shared_state

def main():
    """The main function to run the voice assistant."""
    
    start_session()
    speak("Initializing Assistant.How can I help you sir ?")
    
    while True:
        if shared_state.is_background_task_running:
            continue
            
        query = listen()

        if not query:
            response = "Sorry, I didn't catch that."
            speak(response)
            log_command(None, response, "No Input Detected")
            continue

        query_lower = query.lower()
        response = None
        status = "Command Handled"

        try:
            # --- Command Processing Logic ---
            if any(word in query_lower for word in ['goodbye', 'exit', 'stop','bye']):
                response = "Goodbye Sir! Have a great day."
                speak(response)
                log_command(query, response, "Exit")
                sys.exit()
            elif any(phrase in query_lower for phrase in ['hello', 'hey', 'how are you', 'how r u']):
                response = cmd.handle_greeting(query_lower)
            elif 'add' in query_lower and ('list' in query_lower or 'task' in query_lower):
                task = re.split(r'add|to my list|task', query_lower, flags=re.IGNORECASE)[-1].strip()
                response = cmd.add_todo(task)
            elif ("what's on my" in query_lower or "show me my" in query_lower) and 'list' in query_lower:
                response = cmd.show_todos()
            elif 'task' in query_lower and 'completed' in query_lower:
                if match := re.search(r'task (\d+)', query_lower):
                    response = cmd.complete_todo(match.group(1))
                else:
                    response = "Please specify which task number is completed."
            elif 'timer' in query_lower:
                duration_str = query_lower.replace("set timer for", "").strip()
                response = cmd.set_timer(duration_str)
            elif 'time' in query_lower:
                response = cmd.tell_time()
            elif 'date' in query_lower:
                response = cmd.tell_date()
            elif 'joke' in query_lower:
                response = cmd.tell_joke()
            elif 'wikipedia' in query_lower:
                topic = query_lower.replace("wikipedia", "").strip()
                response = cmd.search_wikipedia(topic)
            elif 'weather in' in query_lower:
                # --- FIX APPLIED HERE ---
                # 1. Split the query to get the part after "in"
                city = query_lower.split('in')[-1].strip()
                # 2. Remove "the " if it's at the beginning of the city name
                if city.startswith("the "):
                    city = city.replace("the ", "", 1)
                
                if city:
                    response = cmd.get_weather(city)
                else:
                    response = "You need to specify a city for the weather."
                    status = "Missing Information"
            elif 'news' in query_lower:
                response = cmd.get_news()
            elif 'open' in query_lower:
                if 'website' in query_lower:
                    website_key = query_lower.replace("open website", "").strip()
                    response = cmd.open_website(website_key)
                else:
                    app_name = query_lower.replace("open", "").strip()
                    response = cmd.open_app(app_name)
            elif 'google' in query_lower or 'search' in query_lower:
                search_term = re.split(r'google|search for|search', query_lower, flags=re.IGNORECASE)[-1].strip()
                response = cmd.search_web(search_term)
            elif 'screenshot' in query_lower:
                response = cmd.take_screenshot()
            elif any(word in query_lower for word in ['volume', 'vol']):
                if match := re.search(r'\d+', query_lower):
                    response = cmd.set_volume(int(match.group(0)))
                else:
                    response = "Please specify a volume level."
            elif 'brightness' in query_lower:
                if match := re.search(r'\d+', query_lower):
                    response = cmd.set_brightness(int(match.group(0)))
                else:
                    response = "Please specify a brightness level."
            elif 'shutdown' in query_lower:
                response = cmd.shutdown_computer()
            elif 'restart' in query_lower:
                response = cmd.restart_computer()
            elif 'sleep' in query_lower:
                response = cmd.sleep_computer()
            elif 'music' in query_lower:
                song = query_lower.replace('music', '').strip()
                if 'pause' in song: response = cmd.pause_music()
                elif 'resume' in song or song == '': response = cmd.resume_music()
                elif 'next' in song: response = cmd.next_track()
                else: response = cmd.play_song(song)
            elif 'email' in query_lower:
                response = cmd.send_email()
            elif 'calculate' in query_lower:
                expression = query_lower.replace("calculate", "").strip()
                response = cmd.calculate(expression)
            else:
                response = "I am not sure how to respond to that."
                status = "Command Not Understood"

            if response:
                speak(response)
                log_command(query, response, status)

        except Exception as e:
            print(f"An unexpected error occurred in main loop: {e}")
            log_command(query, f"ERROR: {e}", "Error")
            speak("Sorry, a critical error occurred.")

if __name__ == "__main__":
    main()

