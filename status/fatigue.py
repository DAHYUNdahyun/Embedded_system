import time
from .constants import SLEEP_RESTORE_TIME

def game_played(status):
    status["fatigue"] = max(0, status["fatigue"] - 15)
    
def check_sleep_restore(status):
    if status["last_sleep_time"] is not None:
        if time.time() - status["last_sleep_time"] >= SLEEP_RESTORE_TIME:
            status["fatigue"] = 80
            status["last_sleep_time"] = None    