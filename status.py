import time

def init_status():
    return {
        "mood": 80,
        "fatigue": 80,
        "hunger": 80,
        "health": 100,
        "evolution": 0,
        "last_sleep_time": None,
        "last_rest_time": None,
        "last_meal_time": time.time(),
        "last_health_check": time.time(),
        "last_evolution_check": time.time(),
        "last_mood_check": time.time(),
    }

def update_mood(status, temperature, humidity):
    now = time.time()
    
    # last_mood_check가 없으면 초기화
    if "last_mood_check" not in status:
        status["last_mood_check"] = now

    if now - status["last_mood_check"] >= 180:  # 3분(180초)마다
        if temperature <= 10 or temperature >= 25 or humidity >= 50:
            status["mood"] = max(0, status["mood"] - 1)
        status["last_mood_check"] = now


def game_played(status):
    status["fatigue"] = max(0, status["fatigue"] - 15)

def start_sleep(status):
    status["last_sleep_time"] = time.time()

def check_sleep_restore(status):
    if status["last_sleep_time"] is not None:
        if time.time() - status["last_sleep_time"] >= 30:
            status["fatigue"] = min(100, 80)
            status["last_sleep_time"] = None

def rest(status):
    now = time.time()
    if status["last_rest_time"] is None:
        status["last_rest_time"] = now
    elif now - status["last_rest_time"] >= 60:
        status["fatigue"] = min(100, status["fatigue"] + 1)
        status["last_rest_time"] = now

def feed(status, rice_count=1):
    status["hunger"] = min(100, status["hunger"] + 5 * rice_count)
    status["last_meal_time"] = time.time()

def slept(status):
    status["hunger"] = max(0, status["hunger"] - 10)

def update_hunger(status):
    now = time.time()
    if now - status["last_meal_time"] >= 180:
        status["hunger"] = max(0, status["hunger"] - 1)
        status["last_meal_time"] = now

def update_health(status):
    now = time.time()
    if now - status["last_health_check"] < 300:
        return
    if status["mood"] <= 0 or status["fatigue"] <= 0 or status["hunger"] <= 0:
        if status["health"] == 100:
            status["health"] -= 10
        else:
            status["health"] = max(0, status["health"] - 5)
    elif status["mood"] >= 80 and status["fatigue"] >= 80 and status["hunger"] >= 80:
        status["health"] = min(100, status["health"] + 1)
    status["last_health_check"] = now

def update_evolution(status):
    now = time.time()
    if now - status["last_evolution_check"] < 300:
        return
    if status["mood"] >= 80 and status["fatigue"] >= 80 and status["hunger"] >= 80:
        status["evolution"] = min(100, status["evolution"] + 1)
    status["last_evolution_check"] = now
