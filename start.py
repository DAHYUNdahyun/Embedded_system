import pygame
import sys
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 0)
PINK = (255, 100, 180)
BLUE = (0, 180, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
BG_PINK = (255, 200, 220)

WIDTH, HEIGHT = 700, 600

def draw_text_center(screen, text, y, color=BLACK, font_obj=None):
    if not font_obj:
        raise ValueError("font_obj must be provided")
    txt = font_obj.render(text, True, color)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y-5))

def draw_start_screen(screen, font_obj, start_select_idx):
    screen.fill(BG_PINK)
    draw_text_center(screen, "Welcome to Tamagotchi!", 50, RED, font_obj=font_obj)

    start_rect = pygame.Rect(WIDTH//2 - 100, 240, 200, 40)
    instr_rect = pygame.Rect(WIDTH//2 - 100, 300, 200, 40)

    if start_select_idx == 0:
        pygame.draw.rect(screen, BLUE, start_rect)
        pygame.draw.rect(screen, GRAY, instr_rect)
    else:
        pygame.draw.rect(screen, GRAY, start_rect)
        pygame.draw.rect(screen, BLUE, instr_rect)

    draw_text_center(screen, "Start Game", 250, WHITE if start_select_idx == 0 else BLACK, font_obj=font_obj)
    draw_text_center(screen, "Instructions", 310, WHITE if start_select_idx == 1 else BLACK, font_obj=font_obj)

def draw_instruction_screen(screen, font_obj):
    screen.fill(WHITE)
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    draw_text_center(screen, "Controls", 80, (255,10,10), title_font)

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
        draw_text_center(screen, line, 140 + i*40, font_obj=font_obj)

def draw_virtual_keyboard(screen, font_obj, vkeys, vk_row, vk_col):
    vk_x, vk_y = 100, HEIGHT - 280
    vk_key_w, vk_key_h = 50, 50
    for r, row in enumerate(vkeys):
        for c, key in enumerate(row):
            rect = pygame.Rect(vk_x + c*vk_key_w, vk_y + r*vk_key_h, vk_key_w - 5, vk_key_h - 5)
            color = BLUE if (r == vk_row and c == vk_col) else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=5)
            disp_key = " " if key == "SPACE" else key
            text_color = WHITE if (r == vk_row and c == vk_col) else BLACK
            key_text = font_obj.render(disp_key, True, text_color)
            screen.blit(key_text, (rect.x + 15, rect.y + 10))
    a = 100
    for i in ["SPACE", "DEL", "ENTER"]:
        rect = pygame.Rect(70 + a, 500, 100, 50)
        a += 110
        color = BLUE if (vk_row == 2 and vkeys[vk_row][vk_col] == i) else GRAY
        pygame.draw.rect(screen, color, rect, border_radius=5)
        text_color = WHITE if (vk_row == 2 and vkeys[vk_row][vk_col] == i) else BLACK
        key_text = font_obj.render(i, True, text_color)
        screen.blit(key_text, (rect.x + 15, rect.y + 10))

def draw_nickname_screen(screen, font_obj, nickname, vkeys, vk_row, vk_col):
    screen.fill(BG_PINK)
    draw_text_center(screen, "Enter your nickname:", 50, font_obj=font_obj)

    input_box = pygame.Rect(WIDTH//2 - 150, 100, 300, 50)
    pygame.draw.rect(screen, WHITE, input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)

    cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
    display_text = nickname + ("_" if cursor_visible else "")
    txt_surface = font_obj.render(display_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    draw_virtual_keyboard(screen, font_obj, vkeys, vk_row, vk_col)

def draw_hello_screen(screen, font_obj, nickname):
    screen.fill(WHITE)
    draw_text_center(screen, f"Hello {nickname}!", HEIGHT//2 - 20, font_obj=font_obj)
    draw_text_center(screen, "Press any key to start", HEIGHT//2 + 20, font_obj=font_obj)
