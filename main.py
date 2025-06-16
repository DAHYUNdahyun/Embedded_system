import pygame
import sys
import random
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

# 전역 상수
WHITE, BLACK, YELLOW, PINK, BLUE, RED, GRAY = (255,255,255), (0,0,0), (255,230,0), (255,100,180), (0,180,255), (255,0,0), (200,200,200)
BG_PINK, GREEN = (255,200,220), (0,200,0)
font = pygame.font.Font("assets/fonts/DungGeunMo.ttf", 24)
rest_text_list = ["휴 식 중", "휴 식 중 .", "휴 식 중 . .", "휴 식 중 . . ."]

# 이미지 정보
emotion_types = ["joy", "eat", "rest", "sad", "zz"]
tama_images = {
    stage: {
        emo: pygame.image.load(f"assets/tama{stage}_{emo}.png").convert_alpha()
        for emo in emotion_types
    } for stage in range(1, 5)
}
tama_img_game = pygame.image.load("assets/tama1_joy.png").convert_alpha()
tama_width, tama_height = tama_images[1]["joy"].get_size()

# 진화 단계 계산
def get_evolution_stage(evo):
    return 1 if evo < 25 else 2 if evo < 50 else 3 if evo < 75 else 4

# 초기 상태
status = init_status()
state = "start"
rest_mode = False
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
font_start = pygame.font.SysFont("Arial", 24, bold=True)
vkeys = [['A','B','C','D','E','F','G','H','I','J'], ['K','L','M','N','O','P','Q','R','S','T'], ['U','V','W','X','Y','Z','SPACE','DEL','ENTER']]
vk_row, vk_col = 0, 0
nickname = ""
start_select_idx = 0

# 게임 관련 변수
player_x, player_y = egg_center_x, egg_y + 400
enemy_spawn_timer, score, lives, shooting_game_over = 0, 0, 3, False
bullets, enemies, bullet_speed, enemy_speed = [], [], 10, 3
runner_x, runner_y = egg_center_x - 50, egg_center_y
runner_speed, gravity = 3, 0.5
obstacles, stars, obstacle_timer, star_timer = [], [], 0, 0
running_score, running_lives, running_game_over = 0, 3, False
is_jumping, jump_velocity, jump_count, MAX_JUMPS = False, 0, 0, 5
dodger_x, dodger_y = 0, 0
dodger_speed, dodger_lives, dodger_score, dodging_game_over = 5, 3, 0, False
falling_objects, falling_timer, falling_interval = [], 0, 40

# 상태 업데이트 함수
def update_all_status():
    update_mood(status, 20, 40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)

def spawn_food(screen_rect):
    margin = 40
    return (
        random.randint(screen_rect.left + margin, screen_rect.right - margin),
        random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    )

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

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    
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
                # 아무 키나 누르면 게임 시작
                state = "main"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
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
                        state = ["shooting", "running", "dodging"][i]

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

            elif state == "dodging" and event.key == pygame.K_r and dodging_game_over:
                dodger_x = 0
                dodger_y = 0
                dodger_score = 0
                dodger_lives = 3
                falling_objects.clear()
                dodging_game_over = False

    if state == "start":
        draw_start_screen(screen, font_start, start_select_idx)

    elif state == "instruction":
        draw_instruction_screen(screen, font_start)

    elif state == "nickname":
        draw_nickname_screen(screen, font_start, nickname, vkeys, vk_row, vk_col)

    elif state == "nickname_done":
        draw_hello_screen(screen, font_start, nickname)

    elif state == "main":
            screen_rect, left_buttons = draw_shell_ui(keys)
    elif state == "game_select":
            screen_rect, left_buttons = draw_shell_ui(keys)
            menu_rects = draw_game_select_menu(screen, screen_rect, font, (BLACK, GRAY))
    elif state == "shooting":
            screen_rect, _ = draw_shell_ui(keys)
            bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over = draw_shooting_game(
                screen, screen_rect, tama_img_game, player_x, player_y,
                bullet_speed, enemy_speed, bullets, enemies, enemy_spawn_timer,
                score, lives, shooting_game_over, font, (RED, BLACK)
            )
    elif state == "running":
            screen_rect, _ = draw_shell_ui(keys)
            ground_y = screen_rect.bottom - 70
            runner_y, is_jumping, jump_velocity, jump_count, obstacles, stars, obstacle_timer, running_score, running_lives, running_game_over = draw_running_game(
                screen, screen_rect, ground_y, gravity, tama_img_game, 80, font, (BLACK, YELLOW, RED),
                runner_y, is_jumping, jump_velocity, jump_count,
                obstacles, stars, obstacle_timer,
                running_score, running_lives, running_game_over
            )
    elif state == "dodging":
            screen_rect, _ = draw_shell_ui(keys)
            dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over = draw_dodging_game(
                screen, screen_rect, tama_img_game, falling_interval, font, (PINK, RED, BLACK),
                dodger_x, dodger_y, falling_objects, falling_timer, dodger_score, dodger_lives, dodging_game_over
            )
    if state == "shooting":
        if keys[pygame.K_LEFT] and player_x > screen_rect.left + 20:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x < screen_rect.right - 20:
            player_x += 5
    if state == "dodging":
        if keys[pygame.K_LEFT] and dodger_x > screen_rect.left + 10:
            dodger_x -= dodger_speed
        if keys[pygame.K_RIGHT] and dodger_x < screen_rect.right - 60:
            dodger_x += dodger_speed
    if keys[pygame.K_LEFT]:
        tama_x -= tama_speed
    if keys[pygame.K_RIGHT]:
        tama_x += tama_speed
    if keys[pygame.K_UP]:
        tama_y -= tama_speed
    if keys[pygame.K_DOWN]:
        tama_y += tama_speed
    if screen_rect:
        tama_x = max(screen_rect.left, min(tama_x, screen_rect.right - tama_width))
        tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height))


    # 휴식 모드 해제 조건
    if not button_pressed[2]:
        rest_mode = False

    # 캐릭터 이동 (메인에서만)
    if not rest_mode and state == "main":
        if keys[pygame.K_LEFT]: tama_x -= tama_speed
        if keys[pygame.K_RIGHT]: tama_x += tama_speed
        if keys[pygame.K_UP]: tama_y -= tama_speed
        if keys[pygame.K_DOWN]: tama_y += tama_speed
        tama_x = max(screen_rect.left, min(tama_x, screen_rect.right - tama_width))
        tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height))

    update_all_status()

    if food:
        fx, fy = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        if ((fx - cx) ** 2 + (fy - cy) ** 2) ** 0.5 < food_radius + 20:
            food = None
            feed(status)
            eating = True
            eat_timer = pygame.time.get_ticks()
    if food:
        pygame.draw.circle(screen, RED, food, food_radius)
    if eating and pygame.time.get_ticks() - eat_timer > 300:
        eating = False

    if state == "main":
        evo = get_evolution_stage(status["evolution"])
        emo = "rest" if rest_mode else "eat" if eating else "sad" if status["mood"] < 50 else "joy"
        screen.blit(tama_images[evo][emo], (tama_x, tama_y))

    if rest_mode:
        rest(status)
        if pygame.time.get_ticks() - rest_text_timer > 500:
            rest_text_index = (rest_text_index + 1) % len(rest_text_list)
            rest_text_timer = pygame.time.get_ticks()
        overlay = pygame.Surface((screen_rect.width, screen_rect.height))
        overlay.set_alpha(100)
        overlay.fill((100, 100, 100))
        screen.blit(overlay, (screen_rect.left, screen_rect.top))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()