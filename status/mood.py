import time
from .constants import MOOD_CHECK_INTERVAL

def update_mood(status, temperature, humidity):
    now = time.time()
    
    # last_mood_check가 없으면 초기화
    if "last_mood_check" not in status:
        status["last_mood_check"] = now

    if now - status["last_mood_check"] >= MOOD_CHECK_INTERVAL:  # 3분(180초)마다
        if temperature <= 10 or temperature >= 25 or humidity >= 50:
            status["mood"] = max(0, status["mood"] - 1)
        status["last_mood_check"] = now