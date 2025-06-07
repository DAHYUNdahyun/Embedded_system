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

# 슈팅게임용 변수수
bullets = []  # 총알 리스트
enemies = []  # 적 리스트
bullet_speed = 10
enemy_speed = 1
enemy_spawn_timer = 0
score = 0
lives = 3
game_over = False

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

# 슈팅게임 전용 다마고치 위치
player_x = egg_center_x
player_y = egg_y + 400  # 알 내부 바닥 근처

# 다마고치 이미지 크기
tama_width, tama_height = 100, 100
tama_speed = 5
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2

# 하트 이미지 불러오기
heart_img = pygame.image.load("assets/real_heart.png").convert_alpha()
empty_heart_img = pygame.image.load("assets/real_empty_heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))
empty_heart_img = pygame.transform.scale(empty_heart_img, (30, 30))


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

# 슈팅 게임용 캐릭터 이미지 준비
tama_img_small = pygame.transform.scale(tama_img, (tama_width // 2, tama_height // 2))

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

    return screen_rect, button_game_rect


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
    global bullets, enemies, enemy_spawn_timer, score, lives, game_over

    # 플레이어 그리기
    screen.blit(tama_img_small, (player_x - tama_width // 4, player_y - tama_height // 4))

    if not game_over:
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
                    game_over = True
            
            # 적이 플레이어와 충돌하면 생명 감소
            dist = ((player_x - enemy[0]) ** 2 + (player_y - enemy[1]) ** 2) ** 0.5
            if dist < 30:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_over = True

        # 충돌 검사
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                dist = ((bullet[0] - enemy[0])**2 + (bullet[1] - enemy[1])**2)**0.5
                if dist < 20:
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    break
    
    # 점수 표시
    score_text = font.render(f"score : {score}", True, BLACK)
    screen.blit(score_text, (screen_rect.left + 13, screen_rect.top + 10))
    
    # 생명 표시
    draw_lives_hearts(screen_rect.left + 10, screen_rect.top + 40, lives)

    # 게임 오버 메시지
    if game_over:
        over_text1 = font.render("Game Over!", True, RED)
        screen.blit(over_text1, (screen_rect.centerx - over_text1.get_width() // 2, screen_rect.centery - 30))
        over_text2 = font.render("Press R to Restart", True, RED)
        screen.blit(over_text2, (screen_rect.centerx - over_text2.get_width() // 2, screen_rect.centery - 5))

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    
    # 상태에 따라 화면 그리기
    if state == "main":
        screen_rect, button_game_rect = draw_shell_ui(keys)
        draw_tamagotchi(tama_x, tama_y)
    elif state == "game_select":
        screen_rect, _ = draw_shell_ui(keys)
        menu_rects = draw_game_select_menu(screen_rect)
    elif state == "shooting":
        screen_rect, _ = draw_shell_ui(keys)
        draw_shooting_game(screen_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        #마우스 클릭 처리
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "main" and button_game_rect.collidepoint(event.pos):
                state = "game_select"
            elif state == "game_select":
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            state = "shooting"
                        elif i == 1:
                            state = "running"
                        elif i == 2:
                            state = "dodging"
        # 키보드 입력 처리
        elif event.type == pygame.KEYDOWN:
            if state == "shooting" and event.key == pygame.K_SPACE:
                bullets.append([player_x, player_y - 30])  # 총알 발사
            elif state == "main" and event.key == pygame.K_SPACE:
                if not food:
                    food = spawn_food(screen_rect)  # 먹이 생성
            elif event.key == pygame.K_r and game_over:
                # 재시작 처리
                bullets.clear()
                enemies.clear()
                score = 0
                lives = 3
                game_over = False

    if state == "shooting":
        if keys[pygame.K_LEFT] and player_x > screen_rect.left + 20:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x < screen_rect.right - 20:
            player_x += 5
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
