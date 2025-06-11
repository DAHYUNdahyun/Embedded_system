import time
from .constants import HEALTH_CHECK_INTERVAL

def update_health(status):
    now = time.time()
    if now - status["last_health_check"] < HEALTH_CHECK_INTERVAL:
        return
    if status["mood"] <= 0 or status["fatigue"] <= 0 or status["hunger"] <= 0:
        if status["health"] == 100:
            status["health"] -= 10
        else:
            status["health"] = max(0, status["health"] - 5)
    elif status["mood"] >= 80 and status["fatigue"] >= 80 and status["hunger"] >= 80:
        status["health"] = min(100, status["health"] + 1)
    status["last_health_check"] = now