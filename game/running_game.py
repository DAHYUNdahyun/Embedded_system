import pygame
import random
from game.draw_heart import draw_lives_hearts

def draw_running_game(screen, screen_rect, background_img, gravity, tama_img_game, coin_img, obstacle_img, obstacle_interval, font, colors,
    runner_y, is_jumping, jump_velocity, jump_count,
    obstacles, stars, obstacle_timer,
    running_score, running_lives, running_game_over):
    BLACK, YELLOW, RED = colors
    
    screen.blit(background_img, screen_rect.topleft)

    # 땅 (하단 70px 영역)
    ground_height = 50
    ground_y = screen_rect.bottom - ground_height


    # 캐릭터 위치 (고정 x)
    runner_x = screen_rect.left + 50

    # 캐릭터 점프 물리 처리
    if is_jumping:
        runner_y += jump_velocity
        jump_velocity += gravity
        
        # 최대 높이 제한
        if runner_y < screen_rect.top:
            runner_y = screen_rect.top
            jump_velocity = 0  # 더 못 올라감

        if runner_y >= ground_y - 50:
            runner_y = ground_y - 50
            is_jumping = False
            jump_velocity = 0
            jump_count = 0

    # 캐릭터 그리기
    screen.blit(tama_img_game, (runner_x, runner_y))

    if not running_game_over:
        # 장애물 생성
        obstacle_timer += 1
        if obstacle_timer >= obstacle_interval:
            # 허들 (바닥 높이)
            obstacles.append({"pos": [screen_rect.right, ground_y-30], "speed": random.randint(4, 6)})
            # 별 (위쪽 높이)
            star_y = ground_y - random.choice([80, 140])
            stars.append({"pos": [screen_rect.right, star_y - 80], "speed": random.randint(3, 6)})
            obstacle_timer = 0

        # 장애물/별 이동 및 충돌
        for obs in obstacles[:]:
            obs["pos"][0] -= obs["speed"]
            screen.blit(obstacle_img, obs["pos"])
            # 충돌 검사
            if runner_y + 50 > obs["pos"][1] and screen_rect.left + 50 < obs["pos"][0] < screen_rect.left + 90:
                obstacles.remove(obs)
                running_lives -= 1
                if running_lives <= 0:
                    running_game_over = True

            elif obs["pos"][0] < screen_rect.left:
                obstacles.remove(obs)

        for star in stars[:]:
            star["pos"][0] -= star["speed"]
            screen.blit(coin_img, (star["pos"][0], star["pos"][1]))
            # 충돌 검사
            if runner_y < star["pos"][1] + 30 and screen_rect.left + 50 < star["pos"][0] < screen_rect.left + 90:
                stars.remove(star)
                running_score += 1
            elif star["pos"][0] < screen_rect.left:
                stars.remove(star)

    # 점수 & 생명
    score_text = font.render(f"score : {running_score}", True, BLACK)
    screen.blit(score_text, (screen_rect.left + 10, screen_rect.top + 10))
    draw_lives_hearts(screen, screen_rect.left + 10, screen_rect.top + 40, running_lives)

    if running_game_over:
        over1 = font.render("Game Over!", True, RED)
        screen.blit(over1, (screen_rect.centerx - over1.get_width() // 2, screen_rect.centery - 30))
        over2 = font.render("Press R to Restart", True, RED)
        screen.blit(over2, (screen_rect.centerx - over2.get_width() // 2, screen_rect.centery - 5))
        
    return (
    runner_y, is_jumping, jump_velocity, jump_count,
    obstacles, stars, obstacle_timer,
    running_score, running_lives, running_game_over
    )