import multiprocessing
import os


def startJarvis():
    print("Process 1 Starting...")
    from main import start
    start()

def listenHotword():
    print("Process 2 Starting...")
    from backend.feature import hotword
    hotword()

if __name__ == "__main__":
    process1 = multiprocessing.Process(target=startJarvis)

    # Gate hotword with env var to avoid microphone conflicts on Windows
    enable_hotword = os.getenv("ENABLE_HOTWORD", "0").lower() in {"1", "true", "yes"}
    process2 = None
    if enable_hotword:
        process2 = multiprocessing.Process(target=listenHotword)

    process1.start()
    if process2:
        process2.start()

    process1.join()

    if process2 and process2.is_alive():
        process2.terminate()
        print("Process 2 terminated.")
        process2.join()

    print("System is terminated.")