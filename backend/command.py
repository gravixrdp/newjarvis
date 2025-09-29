import time
import pyttsx3
import speech_recognition as sr
import eel
from backend.config import MIC_DEVICE_INDEX

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

def _score_device(name: str) -> int:
    nm = (name or "").lower()
    score = 0
    # positives
    if "microphone" in nm or "mic" in nm:
        score += 5
    if "realtek" in nm:
        score += 3
    if "digital" in nm or "array" in nm or "input" in nm:
        score += 2
    if "hands-free" in nm or "headset" in nm:
        score += 1  # may still be valid if it's the only input
    # negatives
    bad_words = ["virtual", "stereo mix", "mapper", "primary", "speakers", "output", "driver", "line out", "headphones"]
    for w in bad_words:
        if w in nm:
            score -= 6
    return score

def _pick_microphone():
    """
    Choose a microphone device index:
      - Use MIC_DEVICE_INDEX if set
      - Else score devices and pick the best input device
      - Else None (default device)
    """
    try:
        devices = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for i, name in enumerate(devices):
            print(f"  [{i}] {name}")
        if MIC_DEVICE_INDEX is not None:
            print(f"Using MIC_DEVICE_INDEX={MIC_DEVICE_INDEX}")
            return MIC_DEVICE_INDEX
        best_idx = None
        best_score = -999
        for i, name in enumerate(devices):
            s = _score_device(name)
            if s > best_score:
                best_score = s
                best_idx = i
        print(f"Auto-selected mic index: {best_idx} (score={best_score})")
        return best_idx
    except Exception as e:
        print(f"Could not enumerate microphones: {e}")
    return None

# Expose the Python function to JavaScript

def takecommand():
    r = sr.Recognizer()
    mic_index = _pick_microphone()
    try:
        source = sr.Microphone(device_index=mic_index)
    except Exception as e:
        print(f"Could not open microphone (index={mic_index}): {e}")
        speak("Microphone not available.")
        return None

    try:
        with source as src:
            print("I'm listening...")
            try:
                eel.DisplayMessage("I'm listening...")
            except Exception:
                pass
            # Tune thresholds
            r.pause_threshold = 0.8
            r.energy_threshold = 100  # lower threshold to detect quieter speech
            r.dynamic_energy_threshold = True
            try:
                r.adjust_for_ambient_noise(src, duration=1.0)
            except AssertionError as e:
                print(f"Ambient noise adjust failed: {e}")
                speak("Microphone is busy. Try selecting another mic in Windows settings.")
                return None
            try:
                # timeout: max wait for speech to start; phrase_time_limit: max length to capture
                audio = r.listen(src, timeout=12, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                print("Timeout: no speech detected.")
                speak("I didn't hear anything.")
                return None
    except AttributeError as e:
        print(f"Microphone context failed (attribute): {e}")
        speak("Microphone not available.")
        return None
    except Exception as e:
        print(f"Microphone context failed: {e}")
        speak("Microphone not available.")
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
