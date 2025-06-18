import pygame
import random
from game.draw_heart import draw_lives_hearts

def draw_dodging_game(screen, screen_rect, tama_img_game, falling_interval, font, colors,
    dodger_x, dodger_y,
    falling_objects, falling_timer,
    dodger_score, dodger_lives, dodging_game_over):
    PINK, RED, BLACK = colors

    # 플레이어 위치 초기화 (처음 진입 시)
    if dodger_x == 0:
        dodger_x = screen_rect.centerx - 30
        dodger_y = screen_rect.bottom - 90

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
    draw_lives_hearts(screen, screen_rect.left + 10, screen_rect.top + 40, dodger_lives)

    if dodging_game_over:
        over1 = font.render("Game Over!", True, RED)
        screen.blit(over1, (screen_rect.centerx - over1.get_width() // 2, screen_rect.centery - 30))
        over2 = font.render("Press R to Restart", True, RED)
        screen.blit(over2, (screen_rect.centerx - over2.get_width() // 2, screen_rect.centery - 5))
        
    return (
    dodger_x, dodger_y,
    falling_objects, falling_timer,
    dodger_score, dodger_lives, dodging_game_over
    )