import pygame

heart_img = None
empty_heart_img = None

def load_heart_images():
    global heart_img, empty_heart_img
    heart_img = pygame.transform.scale(pygame.image.load("assets/real_heart.png").convert_alpha(), (30, 30))
    empty_heart_img = pygame.transform.scale(pygame.image.load("assets/real_empty_heart.png").convert_alpha(), (30, 30))


def draw_lives_hearts(screen, x, y, lives, max_lives=3):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_img, (x + i * 35, y))
        else:
            screen.blit(empty_heart_img, (x + i * 35, y))