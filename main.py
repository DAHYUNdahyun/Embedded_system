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

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 1300, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")
clock = pygame.time.Clock()

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

# 폰트
font = pygame.font.Font("assets/fonts/DungGeunMo.ttf", 24)

# 이미지 로드
scale = 1.5
tama_width, tama_height = int(100 * scale), int(100 * scale)
# 이미지 경로에 진화 단계와 감정 타입이 포함되어야 함
emotion_types = ["joy", "eat", "rest", "sad", "zz"]

# 이미지 딕셔너리: evolution_stage → emotion_type → image
tama_images = {
    stage: {
        emotion: pygame.transform.scale(
            pygame.image.load(f"assets/tama{stage}_{emotion}.png").convert_alpha(),
            (tama_width, tama_height)
        )
        for emotion in emotion_types
    }
    for stage in range(1, 5)  # 1단계~4단계
}


# 레이아웃
egg_w, egg_h = 500, 580
status_w = 250
spacing = 40
total_width = egg_w + status_w + spacing
egg_x = (WIDTH - total_width) // 2
egg_y = (HEIGHT - egg_h) // 2
egg_center_x = egg_x + egg_w // 2
egg_center_y = egg_y + egg_h // 2
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2
tama_speed = 5

# 상태
status = init_status()
rest_mode = False
button_pressed = [False, False, False]
food = None
food_radius = 10
eating = False
eat_timer = 0

# 휴식 텍스트
rest_text_list = ["휴 식 중", "휴 식 중 .", "휴 식 중 . .", "휴 식 중 . . ."]
rest_text_index = 0
rest_text_timer = 0

# 버튼 좌표
left_buttons = []

# 상태바
def draw_status_bar(label, value, x, y, color):
    pygame.draw.rect(screen, GRAY, (x, y, 200, 16))
    pygame.draw.rect(screen, color, (x, y, 200 * value // 100, 16))
    screen.blit(font.render(f"{label}: {int(value)}", True, BLACK), (x, y - 22))

# UI
def draw_shell_ui(keys):
    global left_buttons
    pygame.draw.ellipse(screen, BG_PINK, (egg_x, egg_y, egg_w, egg_h))

    # 화면 안 디스플레이 박스
    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)
    pygame.draw.rect(screen, WHITE, screen_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, screen_rect, 2, border_radius=10)

    # 휴식 텍스트
    if rest_mode:
        text = font.render(rest_text_list[rest_text_index], True, (80, 80, 80))
        screen.blit(text, (screen_rect.centerx - text.get_width() // 2, screen_rect.top + 15))

    screen.blit(font.render("다마고치 친구들", True, RED), (egg_center_x - 100, egg_y + 40))

    # 버튼
    left_buttons = []
    for i in range(3):
        bx = egg_x + 120 + i * 45
        by = egg_y + egg_h - 85
        color = BLACK if button_pressed[i] else GRAY
        pygame.draw.circle(screen, color, (bx, by), 15)
        left_buttons.append(pygame.Rect(bx - 15, by - 15, 30, 30))

    # 방향 버튼
    base_x = egg_center_x + 90
    base_y = egg_y + egg_h - 80
    offset = 22
    for dx, dy, key in [(0, -offset, pygame.K_UP), (0, offset, pygame.K_DOWN),
                        (-offset, 0, pygame.K_LEFT), (offset, 0, pygame.K_RIGHT)]:
        color = BLACK if keys[key] else GRAY
        pygame.draw.rect(screen, color, (base_x + dx, base_y + dy, 12, 12))

    # 상태바 배경 박스 추가
    bg_width = 280
    bg_height = 5 * 45 + 40  # 상태바 5개 + 여백
    bg_x = egg_x + egg_w + spacing - 20
    bg_y = egg_y + (egg_h - bg_height) // 2 - 10

    pygame.draw.rect(screen, (245, 245, 245), (bg_x, bg_y, bg_width, bg_height), border_radius=15)
    pygame.draw.rect(screen, GRAY, (bg_x, bg_y, bg_width, bg_height), 2, border_radius=15)  # 테두리

    # 상태바
    sx = bg_x + 20
    sy = bg_y + 20
    for i, (label, key, color) in enumerate([
        ("기분", "mood", PINK),
        ("체력", "fatigue", BLUE),
        ("배고픔", "hunger", YELLOW),
        ("생명력", "health", RED),
        ("진화", "evolution", GREEN),
    ]):
        draw_status_bar(label, status[key], sx, sy + i * 45, color)

    return screen_rect

# 음식 생성성
def spawn_food(screen_rect):
    margin = 50
    return (random.randint(screen_rect.left + margin, screen_rect.right - margin),
            random.randint(screen_rect.top + margin, screen_rect.bottom - margin))

def update_all_status():
    update_mood(status, temperature=20, humidity=40)
    update_hunger(status)
    check_sleep_restore(status)
    update_health(status)
    update_evolution(status)

# 진화
def get_evolution_stage(evolution_value):
    if evolution_value < 25:
        return 1
    elif evolution_value < 50:
        return 2
    elif evolution_value < 75:
        return 3
    else:
        return 4

# 메인 루프
running = True
while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()
    screen_rect = draw_shell_ui(keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, rect in enumerate(left_buttons):
                if rect.collidepoint(mx, my):
                    button_pressed[i] = not button_pressed[i]
                    if i == 2:
                        rest_mode = not rest_mode
                        print("휴식 모드:", rest_mode)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not food and not rest_mode:
                food = spawn_food(screen_rect)

    # 이동
    if not rest_mode:
        if keys[pygame.K_LEFT]: tama_x -= tama_speed
        if keys[pygame.K_RIGHT]: tama_x += tama_speed
        if keys[pygame.K_UP]: tama_y -= tama_speed
        if keys[pygame.K_DOWN]: tama_y += tama_speed

    # 화면 내부 제한
    tama_x = max(screen_rect.left - 30, min(tama_x, screen_rect.right - tama_width + 21))
    tama_y = max(screen_rect.top, min(tama_y, screen_rect.bottom - tama_height + 30))

    update_all_status()

    # 먹이 충돌 체크
    if food and not rest_mode:
        fx, fy = food
        cx, cy = tama_x + tama_width // 2, tama_y + tama_height // 2
        if ((fx - cx) ** 2 + (fy - cy) ** 2) ** 0.5 < food_radius + 20:
            food = None
            feed(status)
            eating = True
            eat_timer = pygame.time.get_ticks()

    if eating and pygame.time.get_ticks() - eat_timer > 300:
        eating = False

    # 먹이 그리기
    if food:
        pygame.draw.circle(screen, RED, food, food_radius)

    # 진화 단계 계산
    evolution_stage = get_evolution_stage(status["evolution"])

    # 감정 상태에 따라 이미지 선택
    if rest_mode:
        tama_img = tama_images[evolution_stage]["rest"]
    elif eating:
        tama_img = tama_images[evolution_stage]["eat"]
    elif status["mood"] < 50:
        tama_img = tama_images[evolution_stage]["sad"]
    else:
        tama_img = tama_images[evolution_stage]["joy"]

    screen.blit(tama_img, (tama_x, tama_y))

    # 휴식
    if rest_mode:
        rest(status)
        if pygame.time.get_ticks() - rest_text_timer > 500:
            rest_text_index = (rest_text_index + 1) % len(rest_text_list)
            rest_text_timer = pygame.time.get_ticks()
            
        overlay = pygame.Surface((screen_rect.width, screen_rect.height))
        overlay.set_alpha(100)
        overlay.fill((100, 100, 100))
        screen.blit(overlay, (screen_rect.left, screen_rect.top))
    else:
        rest_text_index = 0

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
