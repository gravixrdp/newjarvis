# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)


from compileall import compile_path
import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
import requests
from backend.command import speak
from backend.config import ASSISTANT_NAME, HF_API_TOKEN, HF_MODEL
import sqlite3

from backend.helper import extract_yt_term, remove_words
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()

def _resolve_hf_token_and_model():
    """
    Prefer values from config import; if missing, re-check current env to allow
    setting token via PowerShell $env:... just before run.
    """
    token = HF_API_TOKEN or os.getenv("HF_API_TOKEN")
    model = HF_MODEL or os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
    return token, model

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    # Resolve bundled audio file relative to project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sound_file = os.path.join(base_dir, "frontend", "assets", "audio", "start_sound.mp3")
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except Exception as e:
        # Fallback: speak a small beep if audio missing
        speak("Assistant started")

def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query.lower()
    
    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

def chatBot(query):
    user_input = query.lower()

    # Resolve token/model dynamically to reflect latest env
    token, model = _resolve_hf_token_and_model()
    if token:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {token}"}
            payload = {
                "inputs": user_input,
                "parameters": {
                    "max_new_tokens": 128,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            print(f"Calling HF Inference: model={model}")
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            # Detailed error handling
            if res.status_code == 401:
                speak("Invalid Hugging Face token.")
                return "Invalid token"
            if res.status_code == 403:
                speak("Access denied to the model. Accept model terms on Hugging Face website.")
                return "Model access denied"
            if res.status_code == 503:
                speak("Model is loading, please wait a moment and try again.")
                return "Model loading"
            res.raise_for_status()

            data = res.json()
            # Handle common response formats
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "generated_text" in data[0]:
                    response_text = data[0]["generated_text"]
                else:
                    response_text = str(data[0])
            elif isinstance(data, dict) and "generated_text" in data:
                response_text = data["generated_text"]
            else:
                response_text = str(data)
            print(response_text)
            speak(response_text)
            return response_text
        except Exception as e:
            print(f"HF API error: {e}")
            speak("Chat service is temporarily unavailable.")
            return "Chat service unavailable"

    # Fallback to hugchat cookie-based if configured
    cookie_path = os.path.join("backend", "cookie.json")
    if os.path.exists(cookie_path):
        try:
            chatbot = hugchat.ChatBot(cookie_path=cookie_path)
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)
            response = chatbot.chat(user_input)
            print(response)
            speak(response)
            return response
        except Exception as e:
            print(f"hugchat error: {e}")
            speak("Chat service is temporarily unavailable.")
            return "Chat service unavailable"

    speak("Chat is not configured. Please provide an API token or cookie.")
    return "Chat not configured"