# **Desktop Voice Assistant**

A powerful, command-line-based voice assistant for Windows, built with Python. This assistant is designed to enhance productivity and automate common desktop tasks, providing a hands-free interface for controlling your computer, fetching real-time information, and managing your daily workflow.

## **Features & Commands**

The assistant is capable of understanding a wide range of commands. Here is a list of its functions and how to use them.

### **ℹ️ Information Retrieval**

* **Get Time/Date:** "What time is it?" / "What is the date today?"  
* **Get Weather:** "What's the weather in London?"  
* **Get News:** "Tell me the latest news"  
* **Search Wikipedia:** "Wikipedia Python programming language"  
* **Web Search:** "Search for VIT Bhopal University"  
* **Tell a Joke:** "Tell me a joke"

### **🚀 Productivity**

* **Add To-Do:** "Add 'prepare for project demo' to my to-do list"  
* **Show To-Do List:** "Show me my list"  
* **Set Timer:** "Set a timer for 30 seconds" / "Timer for 1 minute"  
* **Calculator:** "Calculate 15 times 20"  
* **Send Email:** "Send email" *(This will start an interactive session)*

### **⚙️ System & Application Control**

* **Open Application:** "Open notepad" / "Open vs code"  
* **Open Website:** "Open website youtube"  
* **Set Volume:** "Set volume to 70"  
* **Set Brightness:** "Set brightness to 80"  
* **Take Screenshot:** "Take a screenshot"  
* **System Power:** "Shutdown computer" / "Restart computer"

### **🎵 Media Control (Spotify)**

* **Play Music:** "Play music Blinding Lights"  
* **Pause Music:** "Pause music"  
* **Next Track:** "Next track"

## **Setup and Installation**

Follow these steps to get the assistant running on your local machine.

### **1\. Prerequisites**

* **Python 3.8+**  
* A working **microphone**.  
* A **Windows 10/11** operating system.  
* A stable **internet connection** (required for speech recognition and API commands).

### **2\. Clone the Repository**

git clone \[https://github.com/your-username/desktop-voice-assistant.git\](https://github.com/your-username/desktop-voice-assistant.git)  
cd desktop-voice-assistant

### **3\. Install Dependencies**

It is highly recommended to use a Python virtual environment to manage dependencies.

\# Create and activate a virtual environment  
python \-m venv venv  
.\\venv\\Scripts\\activate

\# Install the required packages from the requirements file  
pip install \-r requirements.txt

*(Note: A requirements.txt file should be created containing all the libraries listed in your project report, such as SpeechRecognition, pyttsx3, requests, etc.)*

### **4\. Configure the Assistant**

Before running, you must add your personal API keys and credentials to the config.py file.

1. **Weather API:** Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).  
2. **News API:** Get a free API key from [NewsAPI.org](https://newsapi.org/).  
3. **Spotify:** Create a new application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) to get your Client ID, Client Secret, and set your Redirect URI (use http://127.0.0.1:8888/callback/).  
4. **Email:** Enter your email address and an **"App Password"** for the account you want to send emails from. **Do not use your regular password.** You can generate an App Password in your Google Account's security settings.

Fill in all the required placeholder fields in the config.py file.

## **Usage**

Once the installation and configuration are complete, simply run the main.py script from your terminal:

python main.py  

## 📌Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📌Author

👤 **Anshul Kanodia**

- Github: [@AnshulKan](https://github.com/AnshulKan)
- LinkedIn: [@Anshul-Kanodia](https://www.linkedin.com/in/anshulkanodia/)
- Portfolio: [@Anshul-Kanodia](https://anshulkan.vercel.app/)

## 📌Show your support

Please ⭐️ this repository if this project helped you!

## 📌License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
