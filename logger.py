import logging
from datetime import datetime

LOG_FILE = "assistant_log.txt"

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE)
    ]
)

def log_command(user_query, assistant_response, status="INFO"):
    """Logs the user's command and the assistant's response."""
    # Use a generic level for status to avoid confusion with logging levels
    level = logging.INFO
    if status.upper() == "ERROR":
        level = logging.ERROR
    elif status.upper() == "WARNING":
        level = logging.WARNING
        
    logging.log(level, f"User Query: '{user_query or 'No input detected'}'")
    logging.log(level, f"Assistant Response: '{assistant_response}' | Status: {status}")

def start_session():
    """Logs a separator to mark the beginning of a new session."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    separator = f"\n{'='*25} NEW SESSION STARTED AT {timestamp} {'='*25}\n"
    # The logger is file-based, so this will write directly to the file
    logging.info(separator)

