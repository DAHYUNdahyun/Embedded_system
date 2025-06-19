import pygame
import sys
import random
import board
#import adafruit_dht
import math
import os
import json
#import RPi.GPIO as GPIO
from status.base_status import init_status
from status.mood import update_mood
from status.hunger import update_hunger, feed
from status.fatigue import check_sleep_restore
from status.health import update_health
from status.evolution import update_evolution
from status.actions import rest
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
pygame.display.set_caption("Tamagotchi Style UI")
clock = pygame.time.Clock()
load_heart_images()

SAVE_FOLDER = "save_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# 온습도 센서
#dhtDevice = adafruit_dht.DHT11(board.D17)

# 기울기 센서
tilt_reacted = False
tilt_stage = 0
tilt_timer = 0
TILT_PIN = 27
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(TILT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 전역 상수
WHITE, BLACK, YELLOW, PINK, BLUE, RED, GRAY = (255,255,255), (0,0,0), (255,230,0), (255,100,180), (0,180,255), (255,0,0), (200,200,200)
BG_PINK, GREEN = (255,200,220), (0,200,0)
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

# 위치 계산
egg_w, egg_h = 500, 580
egg_x = (WIDTH - (egg_w + 250 + 40)) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2

# 시작화면
vkeys = [['A','B','C','D','E','F','G','H','I','J'], ['K','L','M','N','O','P','Q','R','S','T'], ['U','V','W','X','Y','Z','SPACE','DEL','ENTER']]
vk_row, vk_col = 0, 0
nickname = ""
start_select_idx = 0

# 게임 관련 변수
player_x, player_y = egg_center_x, egg_y + 400
enemy_spawn_timer, score, lives, shooting_game_over = 0, 0, 3, False
bullets, enemies, bullet_speed, enemy_speed = [], [], 10, 3
runner_x, runner_y = egg_center_x - 50, egg_center_y + 60
runner_speed, gravity = 3, 0.5
obstacles, stars, obstacle_timer, star_timer = [], [], 0, 0
running_score, running_lives, running_game_over = 0, 3, False
is_jumping, jump_velocity, jump_count, MAX_JUMPS = False, 0, 0, 5
dodger_x, dodger_y = 0, 0
dodger_speed, dodger_lives, dodger_score, dodging_game_over = 5, 3, 0, False
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
shooting_game_played = False
running_game_played = False
dodging_game_played = False
prev_shooting_over = False
prev_running_over = False
prev_dodging_over = False
intro_timer = 0           # 게임 설명 시작 시간
selected_game = None      # 선택한 게임 이름 저장

# 상태 업데이트 함수
def update_all_status():
    #update_mood(status, 20, 40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)

def save_status(nickname, status):
    filepath = os.path.join(SAVE_FOLDER, f"{nickname}.json")
    with open(filepath, "w") as f:
        json.dump(status, f)
    print(f"[저장됨] {filepath}")

def load_status(nickname):
    filepath = os.path.join(SAVE_FOLDER, f"{nickname}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        from status.base_status import init_status
        return init_status()

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
    pygame.draw.rect(screen, GRAY, (x, y, 200, 16))
    pygame.draw.rect(screen, color, (x, y, 200 * value // 100, 16))
    screen.blit(font.render(f"{label}: {int(value)}", True, BLACK), (x, y - 22))

def draw_shell_ui(keys):
    left_buttons = []
    pygame.draw.ellipse(screen, BG_PINK, (egg_x, egg_y, egg_w, egg_h))
    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)
    pygame.draw.rect(screen, WHITE, screen_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, screen_rect, 2, border_radius=10)

    if rest_mode:
        text = font.render(rest_text_list[rest_text_index], True, (80, 80, 80))
        screen.blit(text, (screen_rect.centerx - text.get_width() // 2, screen_rect.top + 15))

    screen.blit(font.render("다마고치 친구들", True, RED), (egg_center_x - 100, egg_y + 40))

    for i in range(3):
        bx = egg_x + 120 + i * 45
        by = egg_y + egg_h - 85
        color = BLACK if button_pressed[i] else GRAY
        pygame.draw.circle(screen, color, (bx, by), 15)
        left_buttons.append(pygame.Rect(bx - 15, by - 15, 30, 30))

    base_x, base_y = egg_center_x + 90, egg_y + egg_h - 80
    for dx, dy, key in [(0, -22, pygame.K_UP), (0, 22, pygame.K_DOWN), (-22, 0, pygame.K_LEFT), (22, 0, pygame.K_RIGHT)]:
        pygame.draw.rect(screen, BLACK if keys[key] else GRAY, (base_x + dx, base_y + dy, 12, 12))

    sx, sy = egg_x + egg_w + 40, egg_y + 100
    for i, (label, key, color) in enumerate([
        ("기분", "mood", PINK), ("체력", "fatigue", BLUE), ("배고픔", "hunger", YELLOW),
        ("생명력", "health", RED), ("진화", "evolution", GREEN)
    ]):
        draw_status_bar(label, status[key], sx, sy + i * 45, color)

    return screen_rect, left_buttons

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

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

   
    # 1. 진화 단계 및 감정에 맞는 이미지 선택
    evo = get_evolution_stage(status["evolution"])
    emo = "rest" if rest_mode else "eat" if eating else "sad" if status["mood"] < 50 else "joy"
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
       
    if state in ["main", "game_select", "shooting", "running", "dodging"]:
        screen_rect, left_buttons = draw_shell_ui(keys)
    else:
        screen_rect, left_buttons = None, []
       
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == "start":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    start_select_idx = 1 - start_select_idx  # 0↔1 토글
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if start_select_idx == 0:
                        state = "nickname"
                        nickname = ""
                        vk_row, vk_col = 0, 0
                    else:
                        state = "instruction"
                elif event.key == pygame.K_ESCAPE:
                    running = False

        elif state == "instruction":
            if event.type == pygame.KEYDOWN:
                state = "nickname"
                nickname = ""
                vk_row, vk_col = 0, 0

        elif state == "nickname":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vk_row = (vk_row - 1) % len(vkeys)
                    if vk_col >= len(vkeys[vk_row]):
                        vk_col = len(vkeys[vk_row]) - 1
                elif event.key == pygame.K_DOWN:
                    vk_row = (vk_row + 1) % len(vkeys)
                    if vk_col >= len(vkeys[vk_row]):
                        vk_col = len(vkeys[vk_row]) - 1
                elif event.key == pygame.K_LEFT:
                    vk_col = (vk_col - 1) % len(vkeys[vk_row])
                elif event.key == pygame.K_RIGHT:
                    vk_col = (vk_col + 1) % len(vkeys[vk_row])
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
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
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]

        elif state == "nickname_done":
            if event.type == pygame.KEYDOWN:
                status = load_status(nickname)
                state = "main"
       
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
           
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

        elif event.type == pygame.KEYDOWN:
            if state == "main" and event.key == pygame.K_SPACE:
                if not food:
                    food = spawn_food(screen_rect)

            elif state == "shooting":
                if event.key == pygame.K_SPACE:
                    bullets.append([player_x, player_y - 30])
                elif event.key == pygame.K_r and shooting_game_over:
                    bullets.clear()
                    enemies.clear()
                    score = 0
                    lives = 3
                    shooting_game_over = False
                    shooting_game_played = False
                    prev_shooting_over = False

            elif state == "running":
                if event.key == pygame.K_SPACE and jump_count < MAX_JUMPS:
                    is_jumping = True
                    jump_velocity = -12
                    jump_count += 1
                elif event.key == pygame.K_r and running_game_over:
                    runner_x = screen_rect.left + 50
                    runner_y = egg_center_y
                    obstacles.clear()
                    stars.clear()
                    running_score = 0
                    running_lives = 3
                    running_game_over = False
                    running_game_played = False
                    prev_running_over = False

            elif state == "dodging" and event.key == pygame.K_r and dodging_game_over:
                dodger_x = 0
                dodger_y = 0
                dodger_score = 0
                dodger_lives = 3
                falling_objects.clear()
                dodging_game_over = False
                dodging_game_played = False
                prev_dodging_over = False

    if state == "start":
        draw_start_screen(screen, font, start_select_idx)

    elif state == "instruction":
        draw_instruction_screen(screen, font)

    elif state == "nickname":
        draw_nickname_screen(screen, font, nickname, vkeys, vk_row, vk_col)

    elif state == "nickname_done":
        draw_hello_screen(screen, font, nickname)

    elif state == "main":
            screen_rect, left_buttons = draw_shell_ui(keys)
           
            if not tama_initialized:
                tama_x = screen_rect.centerx - tama_width // 2
                tama_y = screen_rect.centery - tama_height // 2
                tama_initialized = True
               
            # if not tilt_reacted and GPIO.input(TILT_PIN) == GPIO.LOW:
            #     tilt_reacted = True
            #     tilt_stage = 0
            #     tilt_timer = pygame.time.get_ticks()
            #     status["mood"] = max(0, status["mood"] - 5)

            if tilt_reacted:
                now = pygame.time.get_ticks()

                if tilt_stage == 0:
                    shake_offset = math.sin(pygame.time.get_ticks() * 0.02) * 5
                    screen.blit(img_scaled, (tama_x + shake_offset, tama_y))
                   
                    if now - tilt_timer > 1000:
                        tilt_stage = 1
                        tilt_timer = now

                elif tilt_stage == 1:
                    # 2단계: 진화단계에 맞는 dizzy 이미지 보여주기
                    evo = get_evolution_stage(status["evolution"])
                    dizzy_img = pygame.image.load(f"assets/tama{evo}_dizzy.png").convert_alpha()
                    dizzy_scaled = pygame.transform.scale(dizzy_img, (tama_width, tama_height))
                    screen.blit(dizzy_scaled, (tama_x, tama_y))
                    dizzy_text = font.render("I'm dizzy...", True, BLACK)
                    screen.blit(dizzy_text, (tama_x, tama_y - 30))
                    if now - tilt_timer > 2000:
                        tilt_reacted = False  # 원래 상태로 돌아감

            else:
                # tilt_reacted가 아닌 일반 상태일 때만 원래 이미지 그림
                screen.blit(img_scaled, (tama_x, tama_y))
    elif state == "game_select":
            screen_rect, left_buttons = draw_shell_ui(keys)
            menu_rects = draw_game_select_menu(screen, screen_rect, font, (BLACK, GRAY))
    elif state == "shooting":
            screen_rect, _ = draw_shell_ui(keys)
           
            tama_w, tama_h = img_scaled_game.get_size()
           
            bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over = draw_shooting_game(
                screen, screen_rect, shooting_bg, img_scaled_game, enemy_img, player_x, player_y,
                bullet_speed, enemy_speed, bullets, enemies, enemy_spawn_timer,
                score, lives, shooting_game_over, font, (RED, BLACK, WHITE)
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, BLACK)
            screen.blit(text, (exit_button.x + 10, exit_button.y + 5))
           
    elif state == "running":
            screen_rect, _ = draw_shell_ui(keys)
                       
            runner_y, is_jumping, jump_velocity, jump_count, obstacles, stars, obstacle_timer, running_score, running_lives, running_game_over = draw_running_game(
                screen, screen_rect, running_bg, gravity, img_scaled_game, coin_img, 80, font, (BLACK, YELLOW, RED),
                runner_y, is_jumping, jump_velocity, jump_count,
                obstacles, stars, obstacle_timer,
                running_score, running_lives, running_game_over
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, BLACK)
            screen.blit(text, (exit_button.x + 10, exit_button.y + 5))
           
    elif state == "dodging":
            screen_rect, _ = draw_shell_ui(keys)
           
            dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over = draw_dodging_game(
                screen, screen_rect, dodging_bg, img_scaled_game, falling_item_img, falling_interval, font, (PINK, RED, WHITE),
                dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over
            )
           
            exit_button = pygame.Rect(screen_rect.right - 40, screen_rect.top + 10, 30, 30)
            pygame.draw.rect(screen, GRAY, exit_button, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_button, 2, border_radius=8)
            text = font.render("←", True, BLACK)
            screen.blit(text, (exit_button.x + 10, exit_button.y + 5))
    elif state.endswith("_intro"):
            screen_rect, _ = draw_shell_ui(keys)

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
        if keys[pygame.K_LEFT] and player_x - tama_w // 2 > screen_rect.left:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x + tama_w // 2 < screen_rect.right:
            player_x += 5
    if state == "dodging":
        dodge_w, _ = img_scaled_game.get_size()

        if keys[pygame.K_LEFT] and dodger_x > screen_rect.left:
            dodger_x -= dodger_speed
        if keys[pygame.K_RIGHT] and dodger_x + dodge_w < screen_rect.right:
            dodger_x += dodger_speed

    if screen_rect:
        tama_x = max(screen_rect.left, min(tama_x, screen_rect.right - tama_width))
        tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height))


    # 휴식 모드 해제 조건
    if not button_pressed[2]:
        rest_mode = False

    update_all_status()
   
    if state == "main":
        temp, humid = read_temperature_humidity()
        if temp is not None and humid is not None:
            update_mood(status, temp, humid)
            draw_temp_humid_bar(temp, humid)
            print(f"temp: {temp}C, humid: {humid}%, mood: {status['mood']}")

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
            if keys[pygame.K_LEFT]: tama_x -= tama_speed
            if keys[pygame.K_RIGHT]: tama_x += tama_speed
            if keys[pygame.K_UP]: tama_y -= tama_speed
            if keys[pygame.K_DOWN]: tama_y += tama_speed
           
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

    pygame.display.flip()
    clock.tick(60)

save_status(nickname, status)
pygame.quit()
sys.exit()