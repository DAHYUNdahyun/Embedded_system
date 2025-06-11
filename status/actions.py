import time
from .constants import REST_INTERVAL

def start_sleep(status):
    status["last_sleep_time"] = time.time()
    
def rest(status):
    now = time.time()
    if status["last_rest_time"] is None:
        status["last_rest_time"] = now
    elif now - status["last_rest_time"] >= REST_INTERVAL:
        status["fatigue"] = min(100, status["fatigue"] + 1)
        status["last_rest_time"] = now