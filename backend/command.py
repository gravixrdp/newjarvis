import time
import pyttsx3
import speech_recognition as sr
import eel

# Initialize TTS engine once and choose a safe voice index
_engine = None
def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init('sapi5')
        voices = _engine.getProperty('voices') or []
        # Try to pick a common female voice if available, else first available
        preferred_idx = 0
        for i, v in enumerate(voices):
            name = (getattr(v, "name", "") or "").lower()
            gender = (getattr(v, "gender", "") or "").lower()
            if "zira" in name or "female" in gender:
                preferred_idx = i
                break
        if voices:
            try:
                _engine.setProperty('voice', voices[preferred_idx].id)
            except Exception:
                pass
        # Set speaking rate
        try:
            _engine.setProperty('rate', 174)
        except Exception:
            pass
    return _engine

def speak(text):
    text = str(text)
    engine = _get_engine()
    # Update UI message, but don't crash if frontend isn't ready yet
    try:
        eel.DisplayMessage(text)
    except Exception:
        pass
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # As a fallback, just log the text
        print(f"TTS failed, message: {text} ({e})")
    # Mirror to chat UI if available
    try:
        eel.receiverText(text)
    except Exception:
        pass

# Expose the Python function to JavaScript

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        try:
            eel.DisplayMessage("I'm listening...")
        except Exception:
            pass
        # Tune thresholds
        r.pause_threshold = 0.8
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.adjust_for_ambient_noise(source, duration=0.6)
        try:
            # timeout: max wait for speech to start; phrase_time_limit: max length to capture
            audio = r.listen(source, timeout=8, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("Timeout: no speech detected.")
            speak("I didn't hear anything.")
            return None

    try:
        print("Recognizing...")
        try:
            eel.DisplayMessage("Recognizing...")
        except Exception:
            pass
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        try:
            eel.DisplayMessage(query)
        except Exception:
            pass
        speak(query)
    except sr.UnknownValueError:
        print("Speech unintelligible.")
        speak("Sorry, I could not understand.")
        return None
    except sr.RequestError as e:
        print(f"Speech API error: {e}")
        speak("Speech recognition service unavailable.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()



@eel.expose
def takeAllCommands(message=None):
    if message is None:
        query = takecommand()  # If no message is passed, listen for voice input
        if not query:
            return  # Exit if no query is received
        print(query)
        try:
            eel.senderText(query)
        except Exception:
            pass
    else:
        query = message  # If there's a message, use it
        print(f"Message received: {query}")
        try:
            eel.senderText(query)
        except Exception:
            pass
    
    try:
        if query:
            if "open" in query:
                from backend.feature import openCommand
                openCommand(query)
            elif "send message" in query or "call" in query or "video call" in query:
                from backend.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query:
                        flag = 'message'
                        speak("What message to send?")
                        query = takecommand()  # Ask for the message text
                    elif "call" in query:
                        flag = 'call'
                    else:
                        flag = 'video call'
                    whatsApp(Phone, query, flag, name)
            elif "on youtube" in query:
                from backend.feature import PlayYoutube
                PlayYoutube(query)
            else:
                from backend.feature import chatBot
                chatBot(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("Sorry, something went wrong.")
    
    try:
        eel.ShowHood()
    except Exception:
        pass
