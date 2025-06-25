import pygame
import cv2
import numpy as np

# --- 설정 ---
WIDTH, HEIGHT = 800, 600
FPS = 30
VIDEO_NAME = "output.mp4"

# --- 초기화 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- OpenCV VideoWriter 설정 ---
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 또는 'XVID'
video_writer = cv2.VideoWriter(VIDEO_NAME, fourcc, FPS, (WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Pygame 화면 그리기 (예제: 파란 배경 + 빨간 원) ---
    screen.fill((0, 0, 255))
    pygame.draw.circle(screen, (255, 0, 0), (WIDTH//2, HEIGHT//2), 50)
    pygame.display.flip()

    # --- OpenCV로 현재 프레임 저장 ---
    frame = pygame.surfarray.array3d(pygame.display.get_surface())
    frame = np.transpose(frame, (1, 0, 2))  # 가로세로 축 변환
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    video_writer.write(frame)

    clock.tick(FPS)

# --- 정리 ---
video_writer.release()
pygame.quit()
