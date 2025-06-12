import pygame

def draw_game_select_menu(screen, screen_rect, font, colors):
    BLACK, GRAY = colors

    title = font.render("Game Select", True, BLACK)
    screen.blit(title, (screen_rect.centerx - title.get_width() // 2, screen_rect.top + 15))

    options = ["1. Shooting game", "2. Running game", "3. Dodge game"]
    rects = []

    for i, option in enumerate(options):
        box = pygame.Rect(screen_rect.left + 30, screen_rect.top + 60 + i * 100, screen_rect.width - 60, 60)
        pygame.draw.rect(screen, GRAY, box, border_radius=10)
        label = font.render(option, True, BLACK)
        screen.blit(label, (box.centerx - label.get_width() // 2, box.centery - label.get_height() // 2))
        rects.append(box)

    return rects
