import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tamagotchi Style UI")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 0)
PINK = (255, 100, 180)
BLUE = (0, 180, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BG_PINK = (255, 200, 220)

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24, bold=True)

# 상태 변수
state = "start"  # start, instruction, nickname, nickname_done, game

# 가상 키보드 세팅
vkeys = [
    ['A','B','C','D','E','F','G','H','I','J'],
    ['K','L','M','N','O','P','Q','R','S','T'],
    ['U','V','W','X','Y','Z','SPACE','DEL','ENTER']
]
vk_row, vk_col = 0, 0

nickname = ""

# 시작화면 버튼 선택 인덱스 0=start, 1=instruction
start_select_idx = 0

def draw_text_center(text, y, color=BLACK, font_obj=None):
    if not font_obj:
        font_obj = font
    txt = font_obj.render(text, True, color)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y-5))

def draw_start_screen():
    screen.fill(BG_PINK)
    draw_text_center("Welcome to Tamagotchi!", 50, RED, pygame.font.SysFont("Arial", 36, True))

    # 버튼 위치 및 크기
    start_rect = pygame.Rect(WIDTH//2 - 100, 240, 200, 40)
    instr_rect = pygame.Rect(WIDTH//2 - 100, 300, 200, 40)

    # 선택된 버튼 하이라이트
    if start_select_idx == 0:
        pygame.draw.rect(screen, BLUE, start_rect)
        pygame.draw.rect(screen, GRAY, instr_rect)
    else:
        pygame.draw.rect(screen, GRAY, start_rect)
        pygame.draw.rect(screen, BLUE, instr_rect)

    draw_text_center("Start Game", 250, WHITE if start_select_idx == 0 else BLACK)
    draw_text_center("Instructions", 310, WHITE if start_select_idx == 1 else BLACK)

def draw_instruction_screen():
    screen.fill(WHITE)
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    draw_text_center("Controls", 80, (255,10,10), title_font)

    lines = [
        "",
        "Arrow Keys: Move / Navigate",
        "Spacebar: Select",
        "",
        "Move near food to eat it automatically.",
        "",
        "Press any key to continue"
    ]
    for i, line in enumerate(lines):
        draw_text_center(line, 140 + i*40)

def draw_virtual_keyboard():
    vk_x, vk_y = 100, HEIGHT - 280
    vk_key_w, vk_key_h = 50, 50
    for r, row in enumerate(vkeys):
        for c, key in enumerate(row):
            rect = pygame.Rect(vk_x + c*vk_key_w, vk_y + r*vk_key_h, vk_key_w - 5, vk_key_h - 5)
            color = BLUE if (r == vk_row and c == vk_col) else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=5)
            disp_key = " " if key == "SPACE" else key
            text_color = WHITE if (r == vk_row and c == vk_col) else BLACK
            key_text = font.render(disp_key, True, text_color)
            screen.blit(key_text, (rect.x + 15, rect.y + 10))
    a = 100
    for i in ["SPACE", "DEL", "ENTER"]:
        rect = pygame.Rect(70 + a, 500, 100, 50)
        a += 110
        color = BLUE if (r == vk_row and c == vk_col) else GRAY
        pygame.draw.rect(screen, color, rect, border_radius=5)
        disp_key = i
        text_color = WHITE if (r == vk_row and c == vk_col) else BLACK
        key_text = font.render(disp_key, True, text_color)
        screen.blit(key_text, (rect.x + 15, rect.y + 10))

def draw_nickname_screen():
    screen.fill(BG_PINK)
    draw_text_center("Enter your nickname:", 50)

    input_box = pygame.Rect(WIDTH//2 - 150, 100, 300, 50)
    pygame.draw.rect(screen, WHITE, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)

    cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
    display_text = nickname + ("_" if cursor_visible else "")
    txt_surface = font.render(display_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    draw_virtual_keyboard()

def draw_hello_screen():
    screen.fill(WHITE)
    draw_text_center(f"Hello {nickname}!", HEIGHT//2 - 20)
    draw_text_center("Press any key to start", HEIGHT//2 + 20)

def draw_game_screen():
    screen.fill(WHITE)
    draw_text_center(f"Game started! Hello {nickname}", 50)
    # 게임 관련 그리기 여기에 추가 가능

running = True

while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

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
                state = "game"

        elif state == "game":
            # 게임 진행 코드 추가 가능
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    # 상태별 화면 그리기
    if state == "start":
        draw_start_screen()
    elif state == "instruction":
        draw_instruction_screen()
    elif state == "nickname":
        draw_nickname_screen()
    elif state == "nickname_done":
        draw_hello_screen()
    elif state == "game":
        draw_game_screen()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
