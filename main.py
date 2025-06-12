import pygame
import sys
import random
from game_select import draw_game_select_menu
from shooting_game import draw_shooting_game
from running_game import draw_running_game
from dodging_game import draw_dodging_game
from draw_heart import load_heart_images

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")

load_heart_images()

# 전체 흐름(화면 전환)을 관리할 상태 변수
state = "main"  # 또는 "game_select", "shooting", "running", "dodging"

menu_rects = []

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 0)
PINK = (255, 100, 180)
BLUE = (0, 180, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BG_PINK = (255, 200, 220)

# 시계
clock = pygame.time.Clock()

# 알 크기 및 위치
egg_w, egg_h = 500, 580
egg_x = (WIDTH - egg_w) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2

# 다마고치 이미지 크기
tama_width, tama_height = 100, 100
tama_speed = 5
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2

# 먹이 정보
food = None
food_radius = 10
eating = False
eat_timer = 0

# 폰트
font = pygame.font.SysFont("Segoe UI", 24, bold=True)

# 이미지 로드 (tama_stage1)
tama_img = pygame.image.load("assets/tama_stage1.png").convert_alpha()

# 크기 확장
scale_factor = 2
tama_width *= scale_factor
tama_height *= scale_factor
tama_img = pygame.transform.scale(tama_img, (tama_width, tama_height))

# 게임용 캐릭터 이미지 준비
tama_img_game = pygame.transform.scale(tama_img, (60, 60))

# 슈팅게임 전용 변수
bullets = []  # 총알 리스트
enemies = []  # 적 리스트
bullet_speed = 10
enemy_speed = 1
enemy_spawn_timer = 0
score = 0
lives = 3
shooting_game_over = False

# 슈팅게임 전용 다마고치 위치
player_x = egg_center_x
player_y = egg_y + 400  # 알 내부 바닥 근처

# 러닝게임 전용 다마고치 위치
runner_x = egg_center_x - 50
runner_y = egg_center_y

# 러닝게임 전용 변수
runner_speed = 3
obstacles = []
obstacle_timer = 0
obstacle_interval = 80  # 장애물 생성 주기
running_score = 0
running_lives = 3
running_game_over = False

# 점프 관련
is_jumping = False
jump_velocity = 0
gravity = 0.5
jump_count = 0
MAX_JUMPS = 5

# 러닝게임 요소
obstacles = []
stars = []
star_timer = 0
star_interval = 90  # 별이 생성되는 간격
obstacle_timer = 0
obstacle_interval = 80  # 장애물 생성 주기

# 피하기 게임용 변수
dodger_x = 0
dodger_y = 0
dodger_speed = 5
dodger_lives = 3
dodger_score = 0
dodging_game_over = False

falling_objects = []
falling_timer = 0
falling_interval = 40  # 떨어지는 속도

# 위치 재조정
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2

def spawn_food(screen_rect):
    margin = 20
    x = random.randint(screen_rect.left + margin, screen_rect.right - margin)
    y = random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    return (x, y)

def draw_shell_ui(keys):
    pygame.draw.ellipse(screen, BG_PINK, [egg_x, egg_y, egg_w, egg_h])

    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    pygame.draw.rect(screen, WHITE, [screen_x, screen_y, screen_w, screen_h], border_radius=10)
    pygame.draw.rect(screen, BLACK, [screen_x, screen_y, screen_w, screen_h], 2, border_radius=10)
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)

    logo_text = font.render("Tamagotchi Friends", True, RED)
    screen.blit(logo_text, (egg_center_x - logo_text.get_width() // 2, egg_y + 40))

    button_y = egg_y + egg_h - 60
    pygame.draw.circle(screen, GRAY, (egg_center_x - 130, button_y - 30), 15)
    pygame.draw.circle(screen, GRAY, (egg_center_x - 100, button_y + 10), 15)
    
    # 전역으로 버튼 좌표 저장
    button_game_rect = pygame.Rect(egg_center_x - 100 - 15, egg_y + egg_h - 60 + 10 - 15, 30, 30)
    button_main_rect = pygame.Rect(egg_center_x - 130 - 15, button_y - 30 - 15, 30, 30)

    base_x = egg_center_x + 100
    base_y = button_y - 10
    size = 12
    offset = 22

    def draw_dir_button(dx, dy, keycode):
        color = BLACK if keys[keycode] else GRAY
        pygame.draw.rect(screen, color, [base_x + dx, base_y + dy, size, size])

    draw_dir_button(0, -offset, pygame.K_UP)
    draw_dir_button(0, offset, pygame.K_DOWN)
    draw_dir_button(-offset, 0, pygame.K_LEFT)
    draw_dir_button(offset, 0, pygame.K_RIGHT)

    return screen_rect, button_game_rect, button_main_rect


# 다마고치 이미지 그리기
def draw_tamagotchi(x, y):
    screen.blit(tama_img, (x, y))


def draw_food(x, y):
    pygame.draw.circle(screen, RED, (x, y), food_radius)

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    
    # 상태에 따라 화면 그리기
    if state == "main":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        draw_tamagotchi(tama_x, tama_y)
    elif state == "game_select":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        menu_rects = draw_game_select_menu(screen, screen_rect, font, (BLACK, GRAY))
    elif state == "shooting":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        (
            bullets, enemies, enemy_spawn_timer,
            score, lives, shooting_game_over
        ) = draw_shooting_game(
            screen, screen_rect, tama_img_game, player_x, player_y,
            bullet_speed, enemy_speed,
            bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over,
            font, (RED, BLACK)
        )
    elif state == "running":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        ground_y = screen_rect.bottom - 70
        (
            runner_y, is_jumping, jump_velocity, jump_count,
            obstacles, stars, obstacle_timer,
            running_score, running_lives, running_game_over
        ) = draw_running_game(
            screen, screen_rect, ground_y, gravity, tama_img_game, obstacle_interval, font, (BLACK, YELLOW, RED),
            runner_y, is_jumping, jump_velocity, jump_count,
            obstacles, stars, obstacle_timer,
            running_score, running_lives, running_game_over
        )    
    elif state == "dodging":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        (
        dodger_x, dodger_y,
        falling_objects, falling_timer,
        dodger_score, dodger_lives, dodging_game_over
        ) = draw_dodging_game(
            screen, screen_rect, tama_img_game, falling_interval, font, (PINK, RED, BLACK),
            dodger_x, dodger_y,
            falling_objects, falling_timer,
            dodger_score, dodger_lives, dodging_game_over
        )
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        #마우스 클릭 처리
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "main" and button_game_rect.collidepoint(event.pos):
                state = "game_select"
            elif state == "game_select":
                if button_main_rect.collidepoint(event.pos):
                    state = "main"
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            state = "shooting"
                        elif i == 1:
                            state = "running"
                        elif i == 2:
                            state = "dodging"
            elif state in ["shooting", "running", "dodging"]:
                if button_main_rect.collidepoint(event.pos):
                    state = "main"
        # 키보드 입력 처리
        elif event.type == pygame.KEYDOWN:
            if state == "shooting" and event.key == pygame.K_SPACE:
                bullet_x = player_x
                bullet_y = player_y - 30
                bullets.append([bullet_x, bullet_y])
            elif state == "main" and event.key == pygame.K_SPACE:
                if not food:
                    food = spawn_food(screen_rect)  # 먹이 생성
            elif event.key == pygame.K_r and shooting_game_over:
                # 재시작 처리
                bullets.clear()
                enemies.clear()
                score = 0
                lives = 3
                shooting_game_over = False
            elif event.key == pygame.K_r and running_game_over:
                runner_x = screen_rect.left + 50
                runner_y = egg_center_y
                obstacles.clear()
                running_score = 0
                running_lives = 3
                running_game_over = False
            elif state == "running" and event.key == pygame.K_SPACE:
                if jump_count < MAX_JUMPS:
                    is_jumping = True
                    jump_velocity = -12
                    jump_count += 1
            elif event.key == pygame.K_r and dodging_game_over:
                dodger_x = 0
                dodger_y = 0
                dodger_score = 0
                dodger_lives = 3
                falling_objects.clear()
                dodging_game_over = False

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

    if tama_x < screen_rect.left:
        tama_x = screen_rect.left
    if tama_x + tama_width > screen_rect.right:
        tama_x = screen_rect.right - tama_width
    if tama_y < screen_rect.top:
        tama_y = screen_rect.top
    if tama_y + tama_height > screen_rect.bottom:
        tama_y = screen_rect.bottom - tama_height

    eating = False
    if food:
        food_x, food_y = food
        tama_center = (tama_x + tama_width // 2, tama_y + tama_height // 2)
        dist = ((food_x - tama_center[0]) ** 2 + (food_y - tama_center[1]) ** 2) ** 0.5
        if dist < food_radius + 20:
            food = None
            eating = True
            eat_timer = pygame.time.get_ticks()

    if food:
        draw_food(*food)
    # draw_tamagotchi(tama_x, tama_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()