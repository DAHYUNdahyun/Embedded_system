import time

def init_status():
    return {
        "mood": 80,
        "fatigue": 80,
        "hunger": 80,
        "health": 100,
        "evolution": 60,
        "last_sleep_time": None,
        "last_rest_time": None,
        "last_meal_time": time.time(),
        "last_evolution_check": time.time(),
        "last_mood_check": time.time(),
        "mood_fault_time": None,
        "fatigue_fault_time": None,
        "hunger_fault_time": None,
    }
