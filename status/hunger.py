import time
from .constants import HUNGER_CHECK_INTERVAL

def feed(status, rice_count=1):
    status["hunger"] = min(100, status["hunger"] + 5 * rice_count)
    status["last_meal_time"] = time.time()

def slept(status):
    status["hunger"] = max(0, status["hunger"] - 10)

def update_hunger(status):
    now = time.time()
    if now - status["last_meal_time"] >= HUNGER_CHECK_INTERVAL:
        status["hunger"] = max(0, status["hunger"] - 1)
        status["last_meal_time"] = now