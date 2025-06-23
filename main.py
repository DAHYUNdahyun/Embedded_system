import pygame
import sys
import random
import time
import board
import adafruit_dht
import math
import RPi.GPIO as GPIO
import smbus
import json
import os
from status.base_status import init_status
from status.mood import update_mood
from status.hunger import update_hunger, feed
from status.fatigue import check_sleep_restore
from status.health import update_health
from status.evolution import update_evolution
from status.actions import rest, start_sleep
from game.game_select import draw_game_select_menu
from game.shooting_game import draw_shooting_game
from game.running_game import draw_running_game
from game.dodging_game import draw_dodging_game
from game.draw_heart import load_heart_images
from start import draw_start_screen, draw_instruction_screen, draw_virtual_keyboard, draw_nickname_screen, draw_hello_screen

# 초기화
pygame.init()
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Friends")
clock = pygame.time.Clock()
load_heart_images()

dhtDevice = adafruit_dht.DHT11(board.D17)

tilt_reacted = False
tilt_stage = 0
tilt_timer = 0
TILT_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(TILT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
mood_restored = False

LIGHT_PIN = 22
GPIO.setup(LIGHT_PIN, GPIO.IN)

BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer_pwm = GPIO.PWM(BUZZER_PIN, 440)  # 초기 주파수는 440Hz (A음)
buzzer_pwm.start(0)  # 일단 멈춘 상태로 시작

SAVE_FOLDER = "save_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

instruction_page_index = 0

# 전역 상수
WHITE, BLACK, YELLOW, PINK, BLUE, RED, GRAY = (255,255,255), (0,0,0), (255,230,0), (255,100,180), (0,180,255), (255,0,0), (200,200,200)
BG_PINK, GREEN, PASTEL_YELLOW = (255,200,220), (0,200,0), (253, 253, 150)
TEXT_COLOR = (30, 40, 55)
font = pygame.font.Font("assets/fonts/DungGeunMo.ttf", 24)
font_small = pygame.font.Font("assets/fonts/DungGeunMo.ttf", 18)
rest_text_list = ["휴 식 중", "휴 식 중 .", "휴 식 중 . .", "휴 식 중 . . ."]

# 이미지 정보
emotion_types = ["joy", "eat", "rest", "sad", "zz"]
tama_images = {
    stage: {
        emo: pygame.image.load(f"assets/tama{stage}_{emo}.png").convert_alpha()
        for emo in emotion_types
    } for stage in range(1, 5)
}
tama_width, tama_height = tama_images[1]["joy"].get_size()

# 진화 단계 계산
def get_evolution_stage(evo):
    return 1 if evo < 25 else 2 if evo < 50 else 3 if evo < 75 else 4

# 초기 상태
status = init_status()
state = "start"
rest_mode = False
tama_initialized = False
button_pressed = [True, False, False]
menu_rects = []
food, food_radius, eating = None, 10, False
eat_timer, rest_text_index, rest_text_timer = 0, 0, 0
tama_speed = 5
sleeping = False
sleep_detected = False
melody_played = False
show_manual_model = False

# 위치 계산
egg_w, egg_h = 500, 580
egg_x = (WIDTH - (egg_w + 250 + 40)) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2
egg_img = pygame.image.load("assets/egg.png").convert_alpha()
egg_img = pygame.transform.scale(egg_img, (egg_w, egg_h))  # 기존 알 크기와 동일하게

# 시작화면
font_start = pygame.font.SysFont("Arial", 24, bold=True)
vkeys = [['A','B','C','D','E','F','G','H','I','J'], ['K','L','M','N','O','P','Q','R','S','T'], ['U','V','W','X','Y','Z','SPACE','DEL','ENTER']]
vk_row, vk_col = 0, 0
nickname = ""
start_select_idx = 0

# 게임 관련 변수
player_x, player_y = egg_center_x, egg_y + 400
enemy_spawn_timer, score, lives, shooting_game_over = 0, 0, 3, False
bullets, enemies, bullet_speed, enemy_speed = [], [], 20, 3
runner_x, runner_y = egg_center_x - 50, egg_center_y + 60
runner_speed, gravity = 6, 0.5
obstacles, stars, obstacle_timer, star_timer = [], [], 0, 0
running_score, running_lives, running_game_over = 0, 3, False
is_jumping, jump_velocity, jump_count, MAX_JUMPS = False, 0, 0, 5
dodger_x, dodger_y = 0, 0
dodger_speed, dodger_lives, dodger_score, dodging_game_over = 10, 3, 0, False
falling_objects, falling_timer, falling_interval = [], 0, 40    
exit_button = None
shooting_bg = pygame.image.load("assets/game/shooting_background.png").convert()
shooting_bg = pygame.transform.scale(shooting_bg, (320, 350))
enemy_img = pygame.image.load("assets/game/enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))  # 크기 조정
running_bg = pygame.image.load("assets/game/running_background.png").convert()
running_bg = pygame.transform.scale(running_bg, (320, 350))
coin_img = pygame.image.load("assets/game/coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (40, 40))  # 크기 조정
dodging_bg = pygame.image.load("assets/game/dodging_background.png").convert()
dodging_bg = pygame.transform.scale(dodging_bg, (320, 350))
falling_item_img = pygame.image.load("assets/game/falling_item.png").convert_alpha()
falling_item_img = pygame.transform.scale(falling_item_img, (40, 40))
obstacle_img = pygame.image.load("assets/game/obstacle.png").convert_alpha()
obstacle_img = pygame.transform.scale(obstacle_img, (40, 30))
status_bg = pygame.image.load("assets/status_background.png").convert_alpha()
status_bg = pygame.transform.scale(status_bg, (300, 300))  # 상태바 크기에 맞게 조정

shooting_game_played = False
running_game_played = False
dodging_game_played = False
prev_shooting_over = False
prev_running_over = False
prev_dodging_over = False
intro_timer = 0
instruction_timer = None
selected_game = None
show_manual_modal = False
current_manual_page = 0  # 현재 페이지 인덱스

instruction_pages = [ 
[ "📘 소개", "이 다마고치는 단순한 가상 펫이 아닙니다.", "라즈베리파이와 다양한 센서를 활용한", "인터랙티브 스마트 반려 생명체입니다.", "환경을 감지하고, 사용자와 소통하며,", "진화하고, 게임도 함께 즐깁니다!", ], 
[ "📦 주요 기능", "🧠 AI 감정 시스템", "온도/습도에 따라 기분이 변하고,", "음식, 피로, 게임 활동 등으로 상태가 반영됩니다.", "🌡️ DHT11 센서로 온습도 감지", "쾌적한 환경이면 기분이 좋아지고,", "덥거나 습하면 슬퍼져요!" ], 
[ "🔦 조도 센서 (빛 감지)", "어두운 환경에서는 잠에 빠지고,", "밝아지면 자동으로 깨어납니다.", "🎮 세 가지 미니게임 내장", "슈팅 게임 / 러닝 게임 / 회피 게임", "게임으로 피로도를 회복할 수 있어요!" ], 
[ "🍖 먹이주기 기능", "직접 먹이를 소환해서 배불리 먹이세요!", "😵 기울임 반응 (Tilt 센서)", "다마고치를 심하게 흔들면 어지러워해요...", "🔊 부저 멜로디", "모든 상태가 만족스러우면", "기분 좋은 소리를 들려줘요!" ], 
[ "💡 사용 방법", "전원을 켜면 시작 화면이 나타납니다.", "닉네임을 설정하면 부화해요.", "UI 버튼과 터치센서로 상호작용할 수 있어요.", "왼쪽 버튼: 메인 화면", "가운데 버튼: 게임 선택", "오른쪽 버튼: 휴식 모드 전환", "다양한 자극에 반응하는 다마고치를 관찰해보세요!" ] ]

manual_pages = [
    [  # 0번 페이지 - 전체 요약
        "💡 상태바 설명 💡",
        "- 기분: 온도/습도에 따라 변화해요.",
        "- 배고픔: 음식 먹이면 올라가요.",
        "- 피로도: 휴식을 통해 회복돼요.",
        "- 생명력: 피로와 배고픔이 영향을 줘요.",
        "- 진화: 시간이 지나면 자라나요!"
    ],
    [  # 1번 페이지 - 기분 설명
        " 기분 설명",
        "- 다마고치는 게임을 좋아해요!",
        "- 기분은 온도와 습도에 따라 변해요.",
        "- 10 이하 or 25도 이상이면 감소해요.",
        "- 습도가 80% 이상이면 기분이 나빠져요.",
        "- 쾌적한 환경(20~26도, 습도 40~60%) 유지하세요!",
        
    ],
    [  # 2번 페이지 - 배고픔 설명
        " 배고픔 설명",
        "- 시간이 지나면 배고픔이 점점 감소해요.",
        "- 음식 아이템을 먹이면 회복돼요.",
        "- 자고 일어나면 배가 고파져요."
    ],
    [  # 3번 페이지 - 피로도 설명
        " 피로도 설명",
        "- 게임을 하면 피로해져요.",
        "- 휴식 모드를 통해 회복할 수 있어요.",
        "- 수면은 피로도를 빠르게 회복시켜요."
    ],
    [  # 4번 페이지 - 생명력 설명
        " 생명력 설명",
        "- 기분, 배고픔, 피로도가 낮으면 감소해요.",
        "- 상태 관리를 잘해서 생명력을 지켜주세요!"
    ],
    [  # 5번 페이지 - 진화 설명
        " 진화 설명",
        "- 기분, 배고픔, 피로도 관리가 중요해요.",
        "- 진화는 총 4단계로 나뉘어요.",
        "- 진화가 완료되면 새로운 모습이 나타나요!"
    ]
]

TOUCH_KEY_MAP = {
    1: "DOWN",     # 키 1
    2: "RIGHT",    # 키 2
    4: "UP",       # 키 3
    8: "LEFT",     # 키 4
    16: "A",       # 키 5
    32: "B",       # 키 6
    64: "C",       # 키 7
    128: "D",      # 키 8
}

I2C_ADDR = 0x57
bus = smbus.SMBus(1)

def read_touch_keys():
    try:
        value = bus.read_byte(I2C_ADDR)
        return value
    except:
        return 0

def parse_keys(value):
    return [name for bit, name in TOUCH_KEY_MAP.items() if value & bit]

def save_status(nickname, status):
    filepath = os.path.join(SAVE_FOLDER, f"{nickname}.json")
    with open(filepath, "w") as f:
        json.dump(status, f)

def load_status(nickname):
    filepath = os.path.join(SAVE_FOLDER, f"{nickname}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        from status.base_status import init_status
        return init_status()

def play_melody():
    melody = [262, 294, 330, 392, 440, 494, 523]  # 도, 레, 미, 솔, 라, 시, 도
    buzzer_pwm.start(50)  # 50% Duty cycle
    for freq in melody:
        buzzer_pwm.ChangeFrequency(freq)
        time.sleep(0.2)
    buzzer_pwm.stop()

# 상태 업데이트 함수
def update_all_status():
    update_mood(status, 20, 40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)

def spawn_food(screen_rect):
    margin = 60
    x = random.randint(screen_rect.left + margin, screen_rect.right - margin)
    y = random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    image = random.choice(food_images)
    return (x, y), image
   
def read_temperature_humidity():
    try:
        temp = dhtDevice.temperature
        humid = dhtDevice.humidity
        return temp, humid
    except Exception as e:
        print("can't read", e)
        return None, None
       
def draw_temp_humid_bar(temp, humid):
    text = f"temperature: {temp}°C / humidity: {humid}%"
    rendered = font.render(text, True, BLACK)
    text_rect = rendered.get_rect()
    text_rect.topright = (WIDTH - 20, 10)
    screen.blit(rendered, text_rect)

def draw_status_bar(label, value, x, y, color):
    label_surface = font.render(f"{label}: {int(value)}", True, BLACK)
    screen.blit(label_surface, (x, y))

    bar_x = x  # 텍스트와 동일한 x 좌표
    bar_y = y + label_surface.get_height() + 5  # 텍스트 아래 여백 5px

    bar_width = 200
    bar_height = 16

    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
    pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width * value // 100, bar_height), border_radius=5)
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)

def draw_manual_modal():
    global current_manual_page
    modal_w, modal_h = 600, 400
    modal_x = (WIDTH - modal_w) // 2
    modal_y = (HEIGHT - modal_h) // 2

    # 🎨 색상 정의
    MODAL_BG = (245, 245, 255)       # 연한 파스텔 배경
    MODAL_BORDER = (120, 120, 180)   # 테두리 보라
    TEXT_COLOR = (40, 40, 90)        # 차분한 남색

    # 🌕 모달 박스
    pygame.draw.rect(screen, MODAL_BG, (modal_x, modal_y, modal_w, modal_h), border_radius=15)
    pygame.draw.rect(screen, MODAL_BORDER, (modal_x, modal_y, modal_w, modal_h), 3, border_radius=15)

    # 📝 텍스트 출력
    lines = manual_pages[current_manual_page]
    for i, line in enumerate(lines):
        shadow = font.render(line, True, (200, 200, 230))  # 약간 연한 그림자
        text = font.render(line, True, TEXT_COLOR)
        screen.blit(shadow, (modal_x + 31, modal_y + 41 + i * 40))
        screen.blit(text, (modal_x + 30, modal_y + 40 + i * 40))

    # ❌ 닫기 버튼 (동그라미)
    close_btn = pygame.Rect(modal_x + modal_w - 45, modal_y + 15, 25, 25)
    pygame.draw.ellipse(screen, (255, 100, 100), close_btn)
    pygame.draw.ellipse(screen, (180, 0, 0), close_btn, 2)
    x_text = font.render("X", True, (255, 255, 255))
    screen.blit(x_text, (close_btn.x + 5, close_btn.y))

    # ◀ ▶ 페이지 넘김 버튼
    left_btn = pygame.Rect(modal_x + 20, modal_y + modal_h - 50, 30, 30)
    right_btn = pygame.Rect(modal_x + modal_w - 50, modal_y + modal_h - 50, 30, 30)

    pygame.draw.ellipse(screen, (220, 220, 255), left_btn)
    pygame.draw.ellipse(screen, (120, 120, 200), left_btn, 2)

    pygame.draw.ellipse(screen, (220, 220, 255), right_btn)
    pygame.draw.ellipse(screen, (120, 120, 200), right_btn, 2)

    lt = font.render("<", True, (80, 80, 120))
    rt = font.render(">", True, (80, 80, 120))
    screen.blit(lt, (left_btn.x + 8, left_btn.y + 3))
    screen.blit(rt, (right_btn.x + 8, right_btn.y + 3))

    return close_btn, left_btn, right_btn


def draw_shell_ui(keys):
    left_buttons = []
    screen.blit(egg_img, (egg_x, egg_y, egg_w, egg_h))    
    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 125
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)
    pygame.draw.rect(screen, WHITE, screen_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, screen_rect, 2, border_radius=10)

    if rest_mode:
        text = font.render(rest_text_list[rest_text_index], True, (80, 80, 80))
        screen.blit(text, (screen_rect.centerx - text.get_width() // 2, screen_rect.top + 15))

    screen.blit(font.render("다마고치 친구들", True, RED), (egg_center_x - 90, egg_y + 70))

    for i in range(3):
        bx = egg_x + 120 + i * 45
        by = egg_y + egg_h - 85
        color = BLACK if button_pressed[i] else GRAY
        pygame.draw.circle(screen, color, (bx, by), 15)
        left_buttons.append(pygame.Rect(bx - 15, by - 15, 30, 30))

    base_x, base_y = egg_center_x + 90, egg_y + egg_h - 80
    for dx, dy, key in [(0, -22, pygame.K_UP), (0, 22, pygame.K_DOWN), (-22, 0, pygame.K_LEFT), (22, 0, pygame.K_RIGHT)]:
        if 0 <= key < len(keys):
            pygame.draw.rect(screen, BLACK if keys[key] else GRAY, (base_x + dx, base_y + dy, 12, 12))
        else:
            pygame.draw.rect(screen, GRAY, (base_x + dx, base_y + dy, 12, 12))

    status_bg_x = egg_x + egg_w + 60
    status_bg_y = egg_y + 130
    
    manual_box_w = status_bg.get_width()
    manual_box_h = 60
    manual_box_x = status_bg_x
    manual_box_y = status_bg_y - manual_box_h  # 상태바 위에 여백 20

    manual_box_img = pygame.image.load("assets/manual_box_background.png").convert_alpha()
    manual_box_img = pygame.transform.scale(manual_box_img, (300, 80))
    screen.blit(manual_box_img, (manual_box_x, manual_box_y))

    # 책 아이콘 + 텍스트
    book_img = pygame.image.load("assets/manual.png").convert_alpha()
    book_img = pygame.transform.scale(book_img, (32, 32))
    screen.blit(book_img, (manual_box_x + 15, manual_box_y + (manual_box_h - 32) // 2))

    manual_text = font.render("메뉴얼", True, BLACK)
    screen.blit(manual_text, (manual_box_x + 60, manual_box_y + (manual_box_h - manual_text.get_height()) // 2))

    # 클릭 영역 저장
    manual_box_rect = pygame.Rect(manual_box_x, manual_box_y, manual_box_w, manual_box_h)
    screen.blit(status_bg, (status_bg_x, status_bg_y))

    # 상태바 간 간격과 여백 설정
    bar_spacing = 50
    top_bottom_margin = 20
    side_margin = 30

    bar_start_y = status_bg_y + top_bottom_margin
    bar_x = status_bg_x + side_margin  # 좌측 여백 포함

    for i, (label, key, color) in enumerate([
        ("기분", "mood", PINK), ("체력", "fatigue", BLUE), ("배고픔", "hunger", YELLOW),
        ("생명력", "health", RED), ("진화", "evolution", GREEN)
    ]):
        draw_status_bar(label, status[key], bar_x, bar_start_y + i * bar_spacing, color)

    return screen_rect, left_buttons, manual_box_rect

# 음식 이미지 로드
def load_food_images():
    food_image_files = [
        "carrot.png", "chicken.png", "donut.png", "egg_fried.png", "hamburger.png", "pizza.png"
    ]
    food_images = []
    for filename in food_image_files:
        img = pygame.image.load(f"assets/food/" + filename).convert_alpha()
        img = pygame.transform.scale(img, (50, 50))
        food_images.append(img)
    return food_images

food_images = load_food_images()

clock = pygame.time.Clock()
lt = 0


# 메인 루프
running = True
while running:
    screen.fill(WHITE)

    val = read_touch_keys()
    keys = parse_keys(val)
    kys = pygame.key.get_pressed()
    nk = parse_keys(val & ~lt)
   
    # 1. 진화 단계 및 감정에 맞는 이미지 선택
    evo = get_evolution_stage(status["evolution"])
    emo = "zz" if sleeping else ("rest" if rest_mode else "eat" if eating else "sad" if status["mood"] < 50 else "joy")
    image = tama_images[evo][emo]

    # 2. 스케일 비율 적용
    target_width = 100
    iw, ih = image.get_size()
    scale_ratio = target_width / iw
    new_size = (int(iw * scale_ratio), int(ih * scale_ratio))
    img_scaled = pygame.transform.scale(image, new_size)
    img_scaled_width, img_scaled_height = new_size
    tama_width, tama_height = new_size
   
    game_width = 80
    game_ratio = game_width / iw
    img_scaled_game = pygame.transform.scale(image, (int(iw * game_ratio), int(ih * game_ratio)))
       
    if state == "main":
        screen_rect, left_buttons, manual_box_rect = draw_shell_ui(keys)
    elif state in ["game_select", "shooting", "running", "dodging"]:
        screen_rect, left_buttons, _ = draw_shell_ui(keys)  # manual_rect 무시
    else:
        screen_rect, left_buttons = None, []
       
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state == "start":
        if keys:
            if "UP" in nk or "DOWN" in nk:
            #if "UP" in keys or "DOWN" in keys:
                start_select_idx = 1 - start_select_idx  # 0↔1 토글
            elif "D" in keys or "C" in keys:    
                if start_select_idx == 0:
                    state = "nickname"
                    nickname = ""
                    vk_row, vk_col = 0, 0
                else:
                    state = "instruction"
            elif "A" in keys:
                running = False

    elif state == "instruction":
        if instruction_timer is None:
            instruction_timer = time.time()
        if keys and time.time() - instruction_timer >= 3000:
            state = "nickname"
            nickname = ""
            vk_row, vk_col = 0, 0
            instruction_timer = None

    elif state == "nickname":
        if keys:
            if "UP" in nk:
                vk_row = (vk_row - 1) % len(vkeys)
                if vk_col >= len(vkeys[vk_row]):
                    vk_col = len(vkeys[vk_row]) - 1
            elif "DOWN" in nk:
                vk_row = (vk_row + 1) % len(vkeys)
                if vk_col >= len(vkeys[vk_row]):
                    vk_col = len(vkeys[vk_row]) - 1
            elif "LEFT" in nk:
                vk_col = (vk_col - 1) % len(vkeys[vk_row])
            elif "RIGHT" in nk:
                vk_col = (vk_col + 1) % len(vkeys[vk_row])
            elif "D" in nk or "C" in nk:
                key = vkeys[vk_row][vk_col]
                if key == "SPACE":
                    nickname += " "
                elif key == "DEL":
                    nickname = nickname[:-1]
                elif key == "ENTER":
                    if len(nickname.strip()) > 0:
                        state = "nickname_done"
                else:
                    if len(nickname) < 12:
                        nickname += key
            elif "B" in keys:
                nickname = nickname[:-1]

    elif state == "nickname_done":
        if keys:
            status = load_status(nickname)
            state = "main"
   
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()
        
        # ① 매뉴얼 모달이 열려 있고 main 상태일 때: 페이지 넘김 또는 닫기
        if state == "main" and show_manual_modal:
            close_btn, left_btn, right_btn = draw_manual_modal()
            if close_btn.collidepoint((mx, my)):
                show_manual_modal = False
            elif left_btn.collidepoint((mx, my)) and current_manual_page > 0:
                current_manual_page -= 1
            elif right_btn.collidepoint((mx, my)) and current_manual_page < len(manual_pages) - 1:
                current_manual_page += 1
                
        
       # ② 매뉴얼 처음 열기
        elif state == "main":
            if manual_box_rect.collidepoint((mx, my)):
                show_manual_modal = True
                
        
        if exit_button is not None and exit_button.collidepoint((mx, my)):
            if state == "shooting":
                bullets.clear()
                enemies.clear()
                score = 0
                lives = 3
                shooting_game_over = False
                player_x = egg_center_x
                player_y = egg_y + 400
            elif state == "running":
                obstacles.clear()
                stars.clear()
                running_score = 0
                running_lives = 3
                running_game_over = False
                is_jumping = False
                jump_velocity = 0
                jump_count = 0
            elif state == "dodging":
                falling_objects.clear()
                dodger_score = 0
                dodger_lives = 3
                dodging_game_over = False
                dodger_x = 0
                dodger_y = 0
               
            state = "game_select"    
       
        for i, rect in enumerate(left_buttons):
            if rect.collidepoint(mx, my):
                button_pressed = [False, False, False]
                button_pressed[i] = True
                if i == 0:
                    state = "main"
                elif i == 1:
                    state = "game_select"
                elif i == 2:
                    state = "main"
                    rest_mode = True

        if state == "game_select":
            for i, rect in enumerate(menu_rects):
                if rect.collidepoint(mx, my):
                    selected_game = ["shooting", "running", "dodging"][i]
                    state = selected_game + "_intro"
                    intro_timer = pygame.time.get_ticks()
                    
        # manual 버튼은 main 상태일 때만 처리
        if state == "main":
            if show_manual_modal:
                close_btn, left_btn, right_btn = draw_manual_modal()
                if close_btn.collidepoint((mx, my)):
                    show_manual_modal = False
            else:
                if manual_box_rect.collidepoint((mx, my)):
                    show_manual_modal = True


    elif keys:
        if state == "main" and "D" in keys:
            if not food:
                food = spawn_food(screen_rect)

        elif state == "shooting":
            if "D" in nk:
                bullets.append([player_x, player_y - 30])
            elif "A" in keys and shooting_game_over:
                bullets.clear()
                enemies.clear()
                score = 0
                lives = 3
                shooting_game_over = False
                shooting_game_played = False
                prev_shooting_over = False

        elif state == "running":
            if "D" in keys and jump_count < MAX_JUMPS:
                is_jumping = True
                jump_velocity = -12
                jump_count += 1
            elif "A" in keys and running_game_over:
                runner_x = screen_rect.left + 50
                runner_y = egg_center_y
                obstacles.clear()
                stars.clear()
                running_score = 0
                running_lives = 3
                running_game_over = False
                running_game_played = False
                prev_running_over = False

        elif state == "dodging" and "A" in keys and dodging_game_over:
            dodger_x = 0
            dodger_y = 0
            dodger_score = 0
            dodger_lives = 3
            falling_objects.clear()
            dodging_game_over = False
            dodging_game_played = False
            prev_dodging_over = False
           
    lt = val

    if state == "start":
        draw_start_screen(screen, font, start_select_idx)

    elif state == "instruction":
        if not isinstance(instruction_pages, int):
            print(instruction_pages, type(instruction_pages))
        
        draw_instruction_screen(screen, font, instruction_pages, page=instruction_page_index)

        if keys:
            if "LEFT" in nk:
                instruction_page_index = max(0, instruction_page_index- 1)
            elif "RIGHT" in nk:
                instruction_page_index = min(len(instruction_pages) - 1, instruction_page_index+ 1)
            elif "D" in nk or "C" in nk or "ENTER" in nk:
                state = "nickname"
                nickname = ""
                vk_row, vk_col = 0, 0

    elif state == "nickname":
        draw_nickname_screen(screen, font, nickname, vkeys, vk_row, vk_col)

    elif state == "nickname_done":
        draw_hello_screen(screen, font, nickname)

    elif state == "main":
            screen_rect, left_buttons, manual_box_rect = draw_shell_ui(kys)
           
            if not tama_initialized:
                tama_x = screen_rect.centerx - tama_width // 2
                tama_y = screen_rect.centery - tama_height // 2
                tama_initialized = True
               
            if not tilt_reacted and GPIO.input(TILT_PIN) == GPIO.LOW:
                tilt_reacted = True
                tilt_stage = 0
                tilt_timer = pygame.time.get_ticks()
                mood_restored = False

            if tilt_reacted:
                now = pygame.time.get_ticks()

                if tilt_stage == 0:
                    shake_offset = math.sin(pygame.time.get_ticks() * 0.02) * 5
                    screen.blit(img_scaled, (tama_x + shake_offset, tama_y))
                   
                    if now - tilt_timer > 1000:
                        tilt_stage = 1
                        tilt_timer = now
                        mood_updated = False

                elif tilt_stage == 1:
                    # 2단계: 진화단계에 맞는 dizzy 이미지 보여주기
                    evo = get_evolution_stage(status["evolution"])
                    dizzy_img = pygame.image.load(f"assets/tama{evo}_dizzy.png").convert_alpha()
                    dizzy_scaled = pygame.transform.scale(dizzy_img, (tama_width, tama_height))
                    screen.blit(dizzy_scaled, (tama_x, tama_y))
                    dizzy_text = font.render("I'm dizzy...", True, BLACK)
                    screen.blit(dizzy_text, (tama_x, tama_y - 30))
                    
                    if not mood_restored:
                        status["mood"] = min(100, status["mood"] + 5)
                        mood_restored = True
                    
                    if now - tilt_timer > 2000:
                        tilt_reacted = False  # 원래 상태로 돌아감

            else:
                # tilt_reacted가 아닌 일반 상태일 때만 원래 이미지 그림
                screen.blit(img_scaled, (tama_x, tama_y))
    elif state == "game_select":
            screen_rect, left_buttons, manual_box_rect = draw_shell_ui(kys)
            menu_rects = draw_game_select_menu(screen, screen_rect, font, (BLACK, GRAY))
    elif state == "shooting":
            screen_rect, _, _ = draw_shell_ui(kys)
           
            tama_w, tama_h = img_scaled_game.get_size()
           
            bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over = draw_shooting_game(
                screen, screen_rect, shooting_bg, img_scaled_game, enemy_img, player_x, player_y,
                bullet_speed, enemy_speed, bullets, enemies, enemy_spawn_timer,
                score, lives, shooting_game_over, font, (RED, BLACK, WHITE)
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, TEXT_COLOR)
            text_rect = text.get_rect(center=exit_button.center)
            screen.blit(text, text_rect)
           
    elif state == "running":
            screen_rect, _, _ = draw_shell_ui(kys)
                       
            runner_y, is_jumping, jump_velocity, jump_count, obstacles, stars, obstacle_timer, running_score, running_lives, running_game_over = draw_running_game(
                screen, screen_rect, running_bg, gravity, img_scaled_game, coin_img, obstacle_img, 80, font, (BLACK, YELLOW, RED),
                runner_y, is_jumping, jump_velocity, jump_count,
                obstacles, stars, obstacle_timer,
                running_score, running_lives, running_game_over
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, TEXT_COLOR)
            text_rect = text.get_rect(center=exit_button.center)
            screen.blit(text, text_rect)
           
    elif state == "dodging":
            screen_rect, _, _ = draw_shell_ui(kys)
           
            dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over = draw_dodging_game(
                screen, screen_rect, dodging_bg, img_scaled_game, falling_item_img, falling_interval, font, (PINK, RED, WHITE),
                dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, TEXT_COLOR)
            text_rect = text.get_rect(center=exit_button.center)
            screen.blit(text, text_rect)

    elif state.endswith("_intro"):
        screen_rect, _, _ = draw_shell_ui(kys)

        # 어떤 게임 설명인지 판단
        game_name = state.replace("_intro", "")
        bg_map = {
            "shooting": shooting_bg,
            "running": running_bg,
            "dodging": dodging_bg
        }
        instructions = {
            "shooting": ["스페이스바로 총알을 발사하세요!", "적을 맞히면 점수가 올라갑니다!"],
            "running": ["스페이스바로 점프하세요!", "장애물을 피하고 코인을 모으세요!"],
            "dodging": ["좌우 방향키로 움직이세요!", "떨어지는 물체를 피하세요!"]
        }

        # 배경 이미지 출력
        bg = bg_map.get(game_name)
        if bg:
            screen.blit(bg, screen_rect)

        # 설명 문구 줄 단위 처리
        lines = instructions.get(game_name, ["게임 설명이 없습니다"])
        line_height = font_small.get_height()
        box_width = max(font_small.size(line)[0] for line in lines) + 40
        box_height = len(lines) * line_height + 40
        box_x = screen_rect.centerx - box_width // 2
        box_y = screen_rect.centery - box_height // 2

        # 반투명 배경 박스 그리기
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(180)
        box_surface.fill((255, 255, 255))
        screen.blit(box_surface, (box_x, box_y))

        # 텍스트 줄 단위 출력
        for i, line in enumerate(lines):
            rendered = font_small.render(line, True, BLACK)
            text_x = screen_rect.centerx - rendered.get_width() // 2
            text_y = box_y + 20 + i * line_height
            screen.blit(rendered, (text_x, text_y))

        # 3초 후 게임 시작
        if pygame.time.get_ticks() - intro_timer > 3000:
            state = game_name

    if state == "shooting":
        if "LEFT" in keys and player_x - tama_w // 2 > screen_rect.left:
            player_x -= 5
        if "RIGHT" in keys and player_x + tama_w // 2 < screen_rect.right:
            player_x += 5
    if state == "dodging":
        dodge_w, _ = img_scaled_game.get_size()

        if "LEFT" in keys and dodger_x > screen_rect.left:
            dodger_x -= dodger_speed
        if "RIGHT" in keys and dodger_x + dodge_w < screen_rect.right:
            dodger_x += dodger_speed

    if screen_rect:
        tama_x = max(screen_rect.left, min(tama_x, screen_rect.right - tama_width))
        tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height))


    # 휴식 모드 해제 조건
    if not button_pressed[2]:
        rest_mode = False

    update_all_status()

    if state == "main":
        if (status["mood"] >= 90 and status["hunger"] >= 90 and status["fatigue"] >= 90 and not melody_played):
            play_melody()
            melody_played = True
        elif status["mood"] < 90 or status["hunger"] < 90 or status["fatigue"] < 90:
            melody_played = False
        
        temp, humid = read_temperature_humidity()
        if temp is not None and humid is not None:
            update_mood(status, temp, humid)
            draw_temp_humid_bar(temp, humid)
            print(f"temp: {temp}C, humid: {humid}%, mood: {status['mood']}")
           
        light_state = GPIO.input(LIGHT_PIN)
       
        if light_state == GPIO.HIGH and not sleeping:
            print("sleeping")
            sleeping = True
            start_sleep(status)
           
        elif light_state == GPIO.LOW and sleeping:
            print("not sleeping")
            sleeping = False
            status["last_sleep_time"] = None
       
    if food:
        (fx, fy), _ = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        if ((fx - cx) ** 2 + (fy - cy) ** 2) ** 0.5 < food_radius + 20:
            food = None
            feed(status)
            eating = True
            eat_timer = pygame.time.get_ticks()
    if food:
        (fx, fy), food_img = food
        screen.blit(food_img, (fx - food_img.get_width() // 2, fy - food_img.get_height() // 2))
    if eating and pygame.time.get_ticks() - eat_timer > 300:
        eating = False
       
    if state == "main" and not tilt_reacted:
        if not rest_mode:
            if "LEFT" in keys: tama_x -= tama_speed
            if "RIGHT" in keys: tama_x += tama_speed
            if "UP" in keys: tama_y -= tama_speed
            if "DOWN" in keys: tama_y += tama_speed
           
        tama_x = max(screen_rect.left, min(tama_x, screen_rect.right - tama_width))
        tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height))
        if not tilt_reacted:
            screen.blit(img_scaled, (tama_x, tama_y))

    if rest_mode:
        rest(status)
        if pygame.time.get_ticks() - rest_text_timer > 500:
            rest_text_index = (rest_text_index + 1) % len(rest_text_list)
            rest_text_timer = pygame.time.get_ticks()
        overlay = pygame.Surface((screen_rect.width, screen_rect.height))
        overlay.set_alpha(100)
        overlay.fill((100, 100, 100))
        screen.blit(overlay, (screen_rect.left, screen_rect.top))
       
    if sleeping:
        overlay = pygame.Surface((screen_rect.width, screen_rect.height))
        overlay.set_alpha(50)
        overlay.fill((50, 50, 50))
        screen.blit(overlay, (screen_rect.left, screen_rect.top))
       
        sleep_text = font.render("Zzz...", True, WHITE)
        screen.blit(sleep_text, (screen_rect.centerx - sleep_text.get_width() // 2, screen_rect.center[1] -        20))
       
        restored = check_sleep_restore(status)
        if restored:
            sleepnig = False
   
    if state == "shooting" and shooting_game_over and not prev_shooting_over:
            status["mood"] = min(100, status["mood"] + 10)
            status["fatigue"] = min(100, status["fatigue"] - 15)
            shooting_game_played = True
            prev_shooting_over = True
            print("mood +10 fatigue +15")
    if state == "running" and running_game_over and not prev_running_over:
            status["mood"] = min(100, status["mood"] + 10)
            status["fatigue"] = min(100, status["fatigue"] - 15)
            running_game_played = True
            prev_running_over = True
            print("mood +10 fatigue +15")
    if state == "dodging" and dodging_game_over and not prev_dodging_over:
            status["mood"] = min(100, status["mood"] + 10)
            status["fatigue"] = min(100, status["fatigue"] - 15)
            dodging_game_played = True
            prev_dodging_over = True
            print("mood +10 fatigue +15")
            
    if show_manual_modal:
        draw_manual_modal()

    pygame.display.flip()
    clock.tick(60)

buzzer_pwm.stop()
GPIO.cleanup()

save_status(nickname, status)
pygame.quit()
sys.exit()
