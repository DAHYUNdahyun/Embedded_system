import pygame
import sys
import random

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")

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

# 하트 이미지 불러오기
heart_img = pygame.image.load("assets/real_heart.png").convert_alpha()
empty_heart_img = pygame.image.load("assets/real_empty_heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))
empty_heart_img = pygame.transform.scale(empty_heart_img, (30, 30))

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

#게임 선택 화면
def draw_game_select_menu(screen_rect):
    title = font.render("Game Select", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 125))

    options = ["1. Shooting game", "2. Running game", "3. Dodge game"]
    rects = []

    for i, option in enumerate(options):
        box = pygame.Rect(screen_rect.left + 30, screen_rect.top + 60 + i * 100, screen_rect.width - 60, 60)
        pygame.draw.rect(screen, GRAY, box, border_radius=10)
        label = font.render(option, True, BLACK)
        screen.blit(label, (box.centerx - label.get_width() // 2, box.centery - label.get_height() // 2))
        rects.append(box)

    return rects

def draw_lives_hearts(x, y, lives, max_lives=3):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_img, (x + i * 35, y))
        else:
            screen.blit(empty_heart_img, (x + i * 35, y))

def draw_shooting_game(screen_rect):
    global bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over

    # 플레이어 그리기
    screen.blit(tama_img_game, (player_x - 30, player_y - 30))

    if not shooting_game_over:
        # 총알 이동 및 그리기
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            pygame.draw.circle(screen, RED, bullet, 5)
            if bullet[1] < screen_rect.top:
                bullets.remove(bullet)

        # 적 생성 (일정 시간마다)
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60:
            x = random.randint(screen_rect.left + 20, screen_rect.right - 20)
            enemies.append([x, screen_rect.top])
            enemy_spawn_timer = 0

        # 적 이동 및 그리기
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            pygame.draw.rect(screen, BLACK, (enemy[0], enemy[1], 20, 20))
            
            # 적이 바닥에 닿으면 생명 감소
            if enemy[1] > screen_rect.bottom:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    shooting_game_over = True
            
            # 적이 플레이어와 충돌하면 생명 감소
            dist = ((player_x - enemy[0]) ** 2 + (player_y - enemy[1]) ** 2) ** 0.5
            if dist < 30:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    shooting_game_over = True

        # 충돌 검사
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0] - 3, bullet[1] - 3, 6, 6)  # 총알은 지름 6짜리 원으로 가정
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], 20, 20)  # 적은 20x20 정사각형
                
                if bullet_rect.colliderect(enemy_rect):  # 충돌 감지!
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    break  # 하나의 총알이 여러 적 제거 못 하게 break
    
    # 점수 표시
    score_text = font.render(f"score : {score}", True, BLACK)
    screen.blit(score_text, (screen_rect.left + 13, screen_rect.top + 10))
    
    # 생명 표시
    draw_lives_hearts(screen_rect.left + 10, screen_rect.top + 40, lives)

    # 게임 오버 메시지
    if shooting_game_over:
        over_text1 = font.render("Game Over!", True, RED)
        screen.blit(over_text1, (screen_rect.centerx - over_text1.get_width() // 2, screen_rect.centery - 30))
        over_text2 = font.render("Press R to Restart", True, RED)
        screen.blit(over_text2, (screen_rect.centerx - over_text2.get_width() // 2, screen_rect.centery - 5))

def draw_running_game(screen_rect, ground_y):
    global runner_y, is_jumping, jump_velocity, jump_count
    global obstacles, stars, obstacle_timer, running_score, running_lives, running_game_over

    # 캐릭터 위치 (고정 x)
    runner_x = screen_rect.left + 50

    # 캐릭터 점프 물리 처리
    if is_jumping:
        runner_y += jump_velocity
        jump_velocity += gravity
        
        # 최대 높이 제한
        if runner_y < screen_rect.top:
            runner_y = screen_rect.top
            jump_velocity = 0  # 더 못 올라감

        if runner_y >= ground_y:
            runner_y = ground_y
            is_jumping = False
            jump_velocity = 0
            jump_count = 0

    # 캐릭터 그리기
    screen.blit(tama_img_game, (runner_x, runner_y))

    if not running_game_over:
        # 장애물 생성
        obstacle_timer += 1
        if obstacle_timer >= obstacle_interval:
            # 허들 (바닥 높이)
            obstacles.append({"pos": [screen_rect.right, ground_y + 20], "speed": random.randint(4, 6)})
            # 별 (위쪽 높이)
            star_y = ground_y - random.choice([80, 140])
            stars.append({"pos": [screen_rect.right, star_y - 80], "speed": random.randint(3, 6)})
            obstacle_timer = 0

        # 장애물/별 이동 및 충돌
        for obs in obstacles[:]:
            obs["pos"][0] -= obs["speed"]
            pygame.draw.rect(screen, BLACK, (*obs["pos"], 40, 30))  # 허들
            # 충돌 검사
            if runner_y + 50 > obs["pos"][1] and screen_rect.left + 50 < obs["pos"][0] < screen_rect.left + 90:
                obstacles.remove(obs)
                running_lives -= 1
                if running_lives <= 0:
                    running_game_over = True

            elif obs["pos"][0] < screen_rect.left:
                obstacles.remove(obs)

        for star in stars[:]:
            star["pos"][0] -= star["speed"]
            pygame.draw.circle(screen, YELLOW, (star["pos"][0]+15, star["pos"][1]+15), 15)
            # 충돌 검사
            if runner_y < star["pos"][1] + 30 and screen_rect.left + 50 < star["pos"][0] < screen_rect.left + 90:
                stars.remove(star)
                running_score += 1
            elif star["pos"][0] < screen_rect.left:
                stars.remove(star)

    # 점수 & 생명
    score_text = font.render(f"score : {running_score}", True, BLACK)
    screen.blit(score_text, (screen_rect.left + 10, screen_rect.top + 10))
    draw_lives_hearts(screen_rect.left + 10, screen_rect.top + 40, running_lives)

    if running_game_over:
        over1 = font.render("Game Over!", True, RED)
        screen.blit(over1, (screen_rect.centerx - over1.get_width() // 2, screen_rect.centery - 30))
        over2 = font.render("Press R to Restart", True, RED)
        screen.blit(over2, (screen_rect.centerx - over2.get_width() // 2, screen_rect.centery - 5))

def draw_dodging_game(screen_rect):
    global dodger_x, dodger_y, falling_objects, falling_timer
    global dodger_score, dodger_lives, dodging_game_over

    # 플레이어 위치 초기화 (처음 진입 시)
    if dodger_x == 0:
        dodger_x = screen_rect.centerx - 30
        dodger_y = screen_rect.bottom - 70

    # 플레이어 그리기
    screen.blit(tama_img_game, (dodger_x, dodger_y))

    if not dodging_game_over:
        # 떨어지는 물체 생성
        falling_timer += 1
        if falling_timer >= falling_interval:
            x = random.randint(screen_rect.left + 10, screen_rect.right - 40)
            falling_objects.append([x, screen_rect.top])
            falling_timer = 0

        # 물체 이동 및 충돌
        for obj in falling_objects[:]:
            obj[1] += 5
            pygame.draw.circle(screen, PINK, (obj[0] + 15, obj[1] + 15), 15)

            # 충돌
            dist = ((dodger_x + 30 - (obj[0] + 15)) ** 2 + (dodger_y + 30 - (obj[1] + 15)) ** 2) ** 0.5
            if dist < 40:
                falling_objects.remove(obj)
                dodger_lives -= 1
                if dodger_lives <= 0:
                    dodging_game_over = True

            elif obj[1] > screen_rect.bottom:
                falling_objects.remove(obj)
                dodger_score += 1

    # 점수 & 생명
    score_text = font.render(f"score : {dodger_score}", True, BLACK)
    screen.blit(score_text, (screen_rect.left + 10, screen_rect.top + 10))
    draw_lives_hearts(screen_rect.left + 10, screen_rect.top + 40, dodger_lives)

    if dodging_game_over:
        over1 = font.render("Game Over!", True, RED)
        screen.blit(over1, (screen_rect.centerx - over1.get_width() // 2, screen_rect.centery - 30))
        over2 = font.render("Press R to Restart", True, RED)
        screen.blit(over2, (screen_rect.centerx - over2.get_width() // 2, screen_rect.centery - 5))


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
        menu_rects = draw_game_select_menu(screen_rect)
    elif state == "shooting":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        draw_shooting_game(screen_rect)
    elif state == "running":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        ground_y = screen_rect.bottom - 70
        draw_running_game(screen_rect, ground_y)
    elif state == "dodging":
        screen_rect, button_game_rect, button_main_rect  = draw_shell_ui(keys)
        draw_dodging_game(screen_rect)
        
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