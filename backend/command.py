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

def _candidate_mics():
    try:
        devices = sr.Microphone.list_microphone_names()
    except Exception:
        devices = []
    scored = [(i, name, _score_device(name)) for i, name in enumerate(devices)]
    # Prefer explicit env index first, then highest scores
    order = []
    if MIC_DEVICE_INDEX is not None:
        order.append(MIC_DEVICE_INDEX)
    order += [i for i, _, _ in sorted(scored, key=lambda x: x[2], reverse=True)]
    # Keep unique order
    seen = set()
    final = []
    for i in order:
        if i not in seen:
            seen.add(i)
            final.append(i)
    return final, devices

def _open_microphone():
    candidates, devices = _candidate_mics()
    print("Available microphones:")
    for i, name in enumerate(devices):
        print(f"  [{i}] {name}")
    for idx in candidates[:8]:  # Try top 8 candidates max
        try:
            print(f"Trying mic index: {idx}")
            return sr.Microphone(device_index=idx), idx
        except Exception as e:
            print(f"  Mic index {idx} failed: {e}")
            continue
    # Fallback: default device
    try:
        print("Trying default microphone")
        return sr.Microphone(), None
    except Exception as e:
        print(f"  Default mic failed: {e}")
        return None, None

# Expose the Python function to JavaScript

def takecommand():
    r = sr.Recognizer()
    source, used_idx = _open_microphone()
    if source is None:
        # Do not speak error; just log and exit quietly as requested
        print("No working microphone found.")
        return None

    try:
        with source as src:
            print("I'm listening...")
            if used_idx is not None:
                print(f"Using microphone index: {used_idx}")
            try:
                eel.DisplayMessage("I'm listening...")
            except Exception:
                pass
            # Tune thresholds
            r.pause_threshold = 0.8
            r.energy_threshold = 80  # lower threshold to detect quieter speech
            r.dynamic_energy_threshold = True
            try:
                r.adjust_for_ambient_noise(src, duration=1.2)
            except AssertionError as e:
                print(f"Ambient noise adjust failed: {e}")
                # Silent fail per user request
                return None
            try:
                # timeout: max wait for speech to start; phrase_time_limit: max length to capture
                audio = r.listen(src, timeout=12, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                print("Timeout: no speech detected.")
                # Silent per request
                return None
    except AttributeError as e:
        print(f"Microphone context failed (attribute): {e}")
        return None
    except Exception as e:
        print(f"Microphone context failed: {e}")
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
        return None
    except sr.RequestError as e:
        print(f"Speech API error: {e}")
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
