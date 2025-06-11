import time
from .constants import EVOLUTION_CHECK_INTERVAL

def update_evolution(status):
    now = time.time()
    if now - status["last_evolution_check"] < EVOLUTION_CHECK_INTERVAL:
        return
    if status["mood"] >= 80 and status["fatigue"] >= 80 and status["hunger"] >= 80:
        status["evolution"] = min(100, status["evolution"] + 1)
    status["last_evolution_check"] = now