import pygame
import random
from game.draw_heart import draw_lives_hearts

def draw_shooting_game(screen, screen_rect, background_img, tama_img_game, enemy_img, player_x, player_y,
    bullet_speed, enemy_speed,
    bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over,
    font, colors):
    RED, BLACK, WHITE = colors
    
    # 배경 그리기
    screen.blit(background_img, screen_rect.topleft)

    # 적 이미지 크기 가져오기
    enemy_w, enemy_h = enemy_img.get_size()
    tama_w, tama_h = tama_img_game.get_size()

    # 플레이어 그리기 (중앙 기준으로 이미지 배치)
    screen.blit(tama_img_game, (player_x - tama_w // 2, player_y - tama_h // 2))

        
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
            ex, ey = enemy[0], enemy[1]
            screen.blit(enemy_img, (ex - enemy_w // 2, ey - enemy_h // 2))
                        
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
                ex, ey = enemy[0], enemy[1]
                enemy_rect = pygame.Rect(ex - enemy_w // 2, ey - enemy_h // 2, enemy_w, enemy_h)
                
                if bullet_rect.colliderect(enemy_rect):  # 충돌 감지!
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    break  # 하나의 총알이 여러 적 제거 못 하게 break
    
    # 점수 표시
    score_text = font.render(f"score : {score}", True, WHITE)
    screen.blit(score_text, (screen_rect.left + 13, screen_rect.top + 10))
    
    # 생명 표시
    draw_lives_hearts(screen, screen_rect.left + 10, screen_rect.top + 40, lives)

    # 게임 오버 메시지
    if shooting_game_over:
        over_text1 = font.render("Game Over!", True, RED)
        screen.blit(over_text1, (screen_rect.centerx - over_text1.get_width() // 2, screen_rect.centery - 30))
        over_text2 = font.render("R을 눌러 재시작하세요", True, RED)
        screen.blit(over_text2, (screen_rect.centerx - over_text2.get_width() // 2, screen_rect.centery - 5))
    
    return bullets, enemies, enemy_spawn_timer, score, lives, shooting_game_over