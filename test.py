import pygame
import sys
import random

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 700, 600
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
font = pygame.font.SysFont("Arial", 24, bold=True)

# 이미지 로드 (tama_stage1)
tama_img = pygame.image.load("assets/tama_stage1.png").convert_alpha()

# 크기 확장
scale_factor = 2
tama_width *= scale_factor
tama_height *= scale_factor
tama_img = pygame.transform.scale(tama_img, (tama_width, tama_height))

# 위치 재조정
tama_x = egg_center_x - tama_width // 2
tama_y = egg_center_y - tama_height // 2


def spawn_food(screen_rect):
    margin = 20
    x = random.randint(screen_rect.left + margin, screen_rect.right - margin)
    y = random.randint(screen_rect.top + margin, screen_rect.bottom - margin)
    return (x, y)


def draw_hearts(screen_rect, count=3):
    for i in range(count):
        x = screen_rect.left + 20 + i * 30
        y = screen_rect.top + 20
        pygame.draw.circle(screen, RED, (x, y), 8)
        pygame.draw.circle(screen, RED, (x + 10, y), 8)
        points = [(x - 5, y + 5), (x + 15, y + 5), (x + 5, y + 20)]
        pygame.draw.polygon(screen, RED, points)


def draw_shell_ui(keys):
    pygame.draw.ellipse(screen, BG_PINK, [egg_x, egg_y, egg_w, egg_h])

    screen_w, screen_h = 320, 350
    screen_x = egg_center_x - screen_w // 2
    screen_y = egg_y + 110
    pygame.draw.rect(screen, WHITE, [screen_x, screen_y, screen_w, screen_h], border_radius=10)
    pygame.draw.rect(screen, BLACK, [screen_x, screen_y, screen_w, screen_h], 2, border_radius=10)
    screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)

    draw_hearts(screen_rect)

    logo_text = font.render("Tamagotchi Friends", True, RED)
    screen.blit(logo_text, (egg_center_x - logo_text.get_width() // 2, egg_y + 40))

    button_y = egg_y + egg_h - 60
    pygame.draw.circle(screen, GRAY, (egg_center_x - 130, button_y - 30), 15)
    pygame.draw.circle(screen, GRAY, (egg_center_x - 100, button_y + 10), 15)

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

    return screen_rect


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
    screen_rect = draw_shell_ui(keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not food:
                food = spawn_food(screen_rect)

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
    draw_tamagotchi(tama_x, tama_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
