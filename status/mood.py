import time
from .constants import MOOD_CHECK_INTERVAL

def update_mood(status, temperature, humidity):
    now = time.time()
   
    if "last_mood_check" not in status:
        status["last_mood_check"] = 0

    if now - status["last_mood_check"] >= MOOD_CHECK_INTERVAL:  # 3분(180초)마다
        print(f"[mood.py] temp: {temperature}, humid: {humidity}, BEFORE mood: {status['mood']}")
        if temperature <= 10 or temperature >= 25 or humidity >= 50:
            status["mood"] = max(0, status["mood"] - 1)
            print(f"[mood.py] mood down : {status['mood']}")
        else: print("stay mood")
        status["last_mood_check"] = now