import pygame
import sys
import random
from status import *

pygame.init()

# 화면 크기
WIDTH, HEIGHT = 1300, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 0)
PINK = (255, 100, 180)
BLUE = (0, 180, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BG_PINK = (255, 200, 220)
GREEN = (0, 200, 0)

clock = pygame.time.Clock()

# 레이아웃 배치 기준
egg_w, egg_h = 500, 580
status_w = 250
spacing = 40

total_width = egg_w + status_w + spacing
egg_x = (WIDTH - total_width) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2

import pygame
import sys
import random
from status import *

pygame.init()

# 화면 크기
WIDTH, HEIGHT = 1300, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 0)
PINK = (255, 100, 180)
BLUE = (0, 180, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BG_PINK = (255, 200, 220)
GREEN = (0, 200, 0)

clock = pygame.time.Clock()

# 레이아웃 배치 기준
egg_w, egg_h = 500, 580
status_w = 250
spacing = 40

total_width = egg_w + status_w + spacing
egg_x = (WIDTH - total_width) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2

# 캐릭터 이미지
scale = 1.5
tama_width, tama_height = int(100 * scale), int(100 * scale)
tama_img_normal = pygame.transform.scale(pygame.image.load("assets/tama_joy.png").convert_alpha(), (tama_width, tama_height))
tama_img_eat = pygame.transform.scale(pygame.image.load("assets/tama_eat.png").convert_alpha(), (tama_width, tama_height))
tama_img = tama_img_normal
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2
tama_speed = 5

eating = False
eat_timer = 0

# 상태
status = init_status()

rest_mode = False

# 먹이
food = None
food_radius = 10
eating = False

font_path = "assets/fonts/DungGeunMo.ttf"
font = pygame.font.Font(font_path, 24)


rest_text_timer = 0
rest_text_index = 0
rest_text_list = ["휴 식 중", "휴 식 중 .", "휴 식 중 . .", "휴 식 중 . . ."]



def spawn_food(screen_rect):
    margin = 50  # 좌우, 위아래 여백
    x = random.randint(screen_rect.left + margin, screen_rect.right - margin)
    y = random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    return (x, y)




def draw_status_bar(label, value, x, y, color):
    bar_w = 200
    bar_h = 16
    pygame.draw.rect(screen, GRAY, (x, y, bar_w, bar_h))
    pygame.draw.rect(screen, color, (x, y, bar_w * (value / 100), bar_h))
    text = font.render(f"{label}: {int(value)}", True, BLACK)
    screen.blit(text, (x, y - 22))
    

def draw_shell_ui(keys, status):
    pygame.draw.ellipse(screen, BG_PINK, [egg_x, egg_y, egg_w, egg_h])

    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    pygame.draw.rect(screen, WHITE, [screen_x, screen_y, screen_w, screen_h], border_radius=10)
    pygame.draw.rect(screen, BLACK, [screen_x, screen_y, screen_w, screen_h], 2, border_radius=10)
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)

    # 💤 휴식 모드 텍스트 (알 디스플레이 화면 내부 상단)
    if rest_mode:
        rest_surface = font.render(rest_text_list[rest_text_index], True, (80, 80, 80))
        screen.blit(rest_surface, (screen_rect.centerx - rest_surface.get_width() // 2, screen_rect.top + 15))

    logo_text = font.render("다마고치 친구들", True, RED)
    screen.blit(logo_text, (egg_center_x - logo_text.get_width() // 2, egg_y + 40))

    # 버튼 위치
    button_y = egg_y + egg_h - 60
    # 왼쪽 동그라미 버튼 3개 가로 정렬
    left_button_y = egg_y + egg_h - 85  # 기존보다 조금 아래
    left_button_start_x = egg_x + 120    # 더 안쪽으로 시작
    spacing = 45                        # 간격 약간 더 넓게

    # 버튼 좌표 저장 리스트
    global left_buttons
    left_buttons = []

    for i in range(3):
        btn_x = left_button_start_x + i * spacing
        btn_y = left_button_y
        # 그리기
        pygame.draw.circle(screen, GRAY, (btn_x, btn_y), 15)
        # 클릭 판정을 위한 영역 저장
        left_buttons.append(pygame.Rect(btn_x - 15, btn_y - 15, 30, 30))

    base_x = egg_center_x + 90
    base_y = button_y - 20
    size = 12
    offset = 22

    def draw_dir_button(dx, dy, keycode):
        color = BLACK if keys[keycode] else GRAY
        pygame.draw.rect(screen, color, [base_x + dx, base_y + dy, size, size])

    draw_dir_button(0, -offset, pygame.K_UP)
    draw_dir_button(0, offset, pygame.K_DOWN)
    draw_dir_button(-offset, 0, pygame.K_LEFT)
    draw_dir_button(offset, 0, pygame.K_RIGHT)

    # 상태바: 알 기준 우측, 세로 중앙
    status_x = egg_x + egg_w + spacing
    status_gap = 45
    total_h = 5 * status_gap
    status_y = egg_y + (egg_h - total_h) // 2
        
        # 상태바 배경 박스
    bg_width = 280
    bg_height = 5 * 45 + 40  # 상태바 5개 + 여백
    bg_x = egg_x + egg_w + spacing - 20
    bg_y = egg_y + (egg_h - bg_height) // 2 - 10

    pygame.draw.rect(screen, (245, 245, 245), (bg_x, bg_y, bg_width, bg_height), border_radius=15)
    pygame.draw.rect(screen, GRAY, (bg_x, bg_y, bg_width, bg_height), 2, border_radius=15)  # 테두리


    draw_status_bar("기분", status["mood"], status_x, status_y + 0 * status_gap, PINK)
    draw_status_bar("피로도", status["fatigue"], status_x, status_y + 1 * status_gap, BLUE)
    draw_status_bar("배고픔", status["hunger"], status_x, status_y + 2 * status_gap, YELLOW)
    draw_status_bar("생명력", status["health"], status_x, status_y + 3 * status_gap, RED)
    draw_status_bar("진화", status["evolution"], status_x, status_y + 4 * status_gap, GREEN)

    return screen_rect

def draw_tamagotchi(x, y):
    screen.blit(tama_img, (x, y))
    char_bottom_y = tama_y + tama_height


def draw_food(x, y):
    pygame.draw.circle(screen, RED, (x, y), food_radius)

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    screen_rect = draw_shell_ui(keys, status)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, btn_rect in enumerate(left_buttons):
                if btn_rect.collidepoint(mx, my):
                    if i == 2:
                        rest_mode = not rest_mode
                        print("➡️  휴식 모드:", "켜짐" if rest_mode else "꺼짐")
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not food and not rest_mode:
                food = spawn_food(screen_rect)                


        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not food:
                food = spawn_food(screen_rect)

    LEFT_MARGIN = 30
    RIGHT_MARGIN = 21  # 오른쪽만 여유 줌

    tama_x = max(screen_rect.left - LEFT_MARGIN, min(tama_x, screen_rect.right - tama_width + RIGHT_MARGIN))

    BOTTOM_MARGIN = 30
    tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height + BOTTOM_MARGIN))

    update_mood(status, 20, 40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)


    # 휴식 모드 텍스트 애니메이션 (. → .. → ... 순환)
    if rest_mode:
        if pygame.time.get_ticks() - rest_text_timer > 500:  # 500ms 간격
            rest_text_index = (rest_text_index + 1) % len(rest_text_list)
            rest_text_timer = pygame.time.get_ticks()
    else:
        rest_text_index = 0  # 휴식이 꺼지면 초기화

    # 이동 막기
    if not rest_mode:
        if keys[pygame.K_LEFT]: tama_x -= tama_speed
        if keys[pygame.K_RIGHT]: tama_x += tama_speed
        if keys[pygame.K_UP]: tama_y -= tama_speed
        if keys[pygame.K_DOWN]: tama_y += tama_speed

    # 먹이 섭취도 rest_mode일 땐 무시
    if food and not rest_mode:
        fx, fy = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        dist = ((fx - cx)**2 + (fy - cy)**2) ** 0.5
        if dist < food_radius + 20:
            food = None
            feed(status)

            tama_img = tama_img_eat
            eating = True
            eat_timer = pygame.time.get_ticks()



    if food:
        fx, fy = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        dist = ((fx - cx)**2 + (fy - cy)**2) ** 0.5
        if dist < food_radius + 20:
            food = None
            feed(status)
            
            tama_img = tama_img_eat
            eating = True
            eat_timer = pygame.time.get_ticks()


    if eating and pygame.time.get_ticks() - eat_timer > 300:
        tama_img = tama_img_normal
        eating = False
    if food:
        draw_food(*food)
    draw_tamagotchi(tama_x, tama_y)

    if rest_mode:
        overlay = pygame.Surface((screen_rect.width, screen_rect.height))
        overlay.set_alpha(100)  # 투명도 조절
        overlay.fill((100, 100, 100))  # 회색
        screen.blit(overlay, (screen_rect.left, screen_rect.top))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


# 상태
status = init_status()

rest_mode = False

# 먹이
food = None
food_radius = 10
eating = False

font = pygame.font.SysFont("Arial", 24, bold=True)

def spawn_food(screen_rect):
    margin = 50  # 좌우, 위아래 여백
    x = random.randint(screen_rect.left + margin, screen_rect.right - margin)
    y = random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    return (x, y)




def draw_status_bar(label, value, x, y, color):
    bar_w = 200
    bar_h = 16
    pygame.draw.rect(screen, GRAY, (x, y, bar_w, bar_h))
    pygame.draw.rect(screen, color, (x, y, bar_w * (value / 100), bar_h))
    text = font.render(f"{label}: {int(value)}", True, BLACK)
    screen.blit(text, (x, y - 22))
    

def draw_shell_ui(keys, status):
    pygame.draw.ellipse(screen, BG_PINK, [egg_x, egg_y, egg_w, egg_h])

    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    pygame.draw.rect(screen, WHITE, [screen_x, screen_y, screen_w, screen_h], border_radius=10)
    pygame.draw.rect(screen, BLACK, [screen_x, screen_y, screen_w, screen_h], 2, border_radius=10)
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)
    # draw_shell_ui 내부, screen_rect 만들고 나서 아래 추가
    pygame.draw.line(screen, (0, 0, 255), (screen_rect.left, screen_rect.bottom), (screen_rect.right, screen_rect.bottom), 2)



    logo_text = font.render("Tamagotchi Friends", True, RED)
    screen.blit(logo_text, (egg_center_x - logo_text.get_width() // 2, egg_y + 40))

    # 버튼 위치
    button_y = egg_y + egg_h - 60
    # 왼쪽 동그라미 버튼 3개 가로 정렬
    left_button_y = egg_y + egg_h - 85  # 기존보다 조금 아래
    left_button_start_x = egg_x + 120    # 더 안쪽으로 시작
    spacing = 45                        # 간격 약간 더 넓게

    # 버튼 좌표 저장 리스트
    global left_buttons
    left_buttons = []

    for i in range(3):
        btn_x = left_button_start_x + i * spacing
        btn_y = left_button_y
        # 그리기
        pygame.draw.circle(screen, GRAY, (btn_x, btn_y), 15)
        # 클릭 판정을 위한 영역 저장
        left_buttons.append(pygame.Rect(btn_x - 15, btn_y - 15, 30, 30))

    base_x = egg_center_x + 90
    base_y = button_y - 20
    size = 12
    offset = 22

    def draw_dir_button(dx, dy, keycode):
        color = BLACK if keys[keycode] else GRAY
        pygame.draw.rect(screen, color, [base_x + dx, base_y + dy, size, size])

    draw_dir_button(0, -offset, pygame.K_UP)
    draw_dir_button(0, offset, pygame.K_DOWN)
    draw_dir_button(-offset, 0, pygame.K_LEFT)
    draw_dir_button(offset, 0, pygame.K_RIGHT)

    # 상태바: 알 기준 우측, 세로 중앙
    status_x = egg_x + egg_w + spacing
    status_gap = 45
    total_h = 5 * status_gap
    status_y = egg_y + (egg_h - total_h) // 2
        
    # 상태바 배경 박스
    bg_width = 280
    bg_height = 5 * 45 + 40  # 상태바 5개 + 여백
    bg_x = egg_x + egg_w + spacing - 20
    bg_y = egg_y + (egg_h - bg_height) // 2 - 10

    pygame.draw.rect(screen, (245, 245, 245), (bg_x, bg_y, bg_width, bg_height), border_radius=15)
    pygame.draw.rect(screen, GRAY, (bg_x, bg_y, bg_width, bg_height), 2, border_radius=15)  # 테두리


    draw_status_bar("기분", status["mood"], status_x, status_y + 0 * status_gap, PINK)
    draw_status_bar("피로도", status["fatigue"], status_x, status_y + 1 * status_gap, BLUE)
    draw_status_bar("배고픔", status["hunger"], status_x, status_y + 2 * status_gap, YELLOW)
    draw_status_bar("생명력", status["health"], status_x, status_y + 3 * status_gap, RED)
    draw_status_bar("진화", status["evolution"], status_x, status_y + 4 * status_gap, GREEN)

    return screen_rect

def draw_tamagotchi(x, y):
    screen.blit(tama_img, (x, y))
    char_bottom_y = tama_y + tama_height
    pygame.draw.line(screen, (255, 0, 0), (tama_x, char_bottom_y), (tama_x + tama_width, char_bottom_y), 2)


def draw_food(x, y):
    pygame.draw.circle(screen, RED, (x, y), food_radius)

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    screen_rect = draw_shell_ui(keys, status)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, btn_rect in enumerate(left_buttons):
                if btn_rect.collidepoint(mx, my):
                    if i == 2:
                        print("➡️  휴식 버튼 클릭됨")
                        rest_mode = True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not food:
                food = spawn_food(screen_rect)



    if keys[pygame.K_LEFT]: tama_x -= tama_speed
    if keys[pygame.K_RIGHT]: tama_x += tama_speed
    if keys[pygame.K_UP]: tama_y -= tama_speed
    if keys[pygame.K_DOWN]: tama_y += tama_speed

    LEFT_MARGIN = 30
    RIGHT_MARGIN = 21  # 오른쪽만 여유 줌

    tama_x = max(screen_rect.left - LEFT_MARGIN, min(tama_x, screen_rect.right - tama_width + RIGHT_MARGIN))

    BOTTOM_MARGIN = 30
    tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height + BOTTOM_MARGIN))

    update_mood(status, 20, 40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)

    # 먹이 충돌 체크 및 먹는 처리
    if food:
        fx, fy = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        dist = ((fx - cx)**2 + (fy - cy)**2) ** 0.5
        if dist < food_radius + 20:
            food = None
            feed(status)

            # 🔹 먹는 이미지로 변경
            tama_img = tama_img_eat
            eating = True
            eat_timer = pygame.time.get_ticks()

    # 🔹 먹는 이미지 유지 시간 조절 (300ms 후 원래 이미지로 복귀)
    if eating and pygame.time.get_ticks() - eat_timer > 300:
        tama_img = tama_img_normal
        eating = False

    # 🔹 먹이 그리기 (남아있을 때만)
    if food:
        draw_food(*food)

    # 🔹 타마고치 그리기 (항상)
    draw_tamagotchi(tama_x, tama_y)
    
    if rest_mode:
        rest(status)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
