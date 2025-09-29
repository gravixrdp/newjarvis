import eel

# Text-only output: no TTS, no microphone usage.

def speak(text):
    text = str(text)
    print(text)
    try:
        eel.DisplayMessage(text)
    except Exception:
        pass
    try:
        eel.receiverText(text)
    except Exception:
        pass


@eel.expose
def takeAllCommands(message=None):
    """
    Text-only command handler.
    Voice input is disabled to avoid microphone errors.
    """
    if not message:
        # Nothing to do if no message provided.
        return

    query = str(message).strip().lower()
    try:
        eel.senderText(query)
    except Exception:
        pass

    try:
        if "open" in query:
            from backend.feature import openCommand
            openCommand(query)

        elif "send message" in query or "call" in query or "video call" in query:
            from backend.feature import findContact, whatsApp
            flag = ""
            Phone, name = findContact(query)
            if Phone != 0:
                if "send message" in query:
                    flag = "message"
                    speak("What message to send? Type your message in the chat.")
                    # In text-only mode, we don't capture microphone. Expect next text input as message.
                    return
                elif "call" in query:
                    flag = "call"
                else:
                    flag = "video call"
                whatsApp(Phone, "", flag, name)

        elif "on youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)

        else:
            from backend.feature import chatBot
            chatBot(query)

    except Exception as e:
        print(f"An error occurred: {e}")
        speak("Sorry, something went wrong.")

    try:
        eel.ShowHood()
    except Exception:
        pass
