import pygame
import sys

# 1. 초기화 및 설정
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Teleporting Circle Game")

# 색상 및 속도 설정
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0) # 실험용 색상

# 2. 변수 설정 (원의 위치와 크기)
x = SCREEN_WIDTH // 2  # 화면 중앙 x
y = SCREEN_HEIGHT // 2 # 화면 중앙 y
radius = 50
speed = 7

clock = pygame.time.Clock()
running = True

# 3. 게임 루프 시작
while running:
    # [이벤트 처리] 사용자가 창을 닫는지 확인
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # [입력 처리] 키보드 화살표 키 상태 확인
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    # [로직 처리] 화면 밖으로 나갈 때 텔레포트 (루핑)
    # 오른쪽으로 나갈 때
    if x > SCREEN_WIDTH + radius:
        x = -radius
    # 왼쪽으로 나갈 때
    elif x < -radius:
        x = SCREEN_WIDTH + radius
        
    # 아래로 나갈 때
    if y > SCREEN_HEIGHT + radius:
        y = -radius
    # 위로 나갈 때
    elif y < -radius:
        y = SCREEN_HEIGHT + radius

    # [그리기 처리]
    screen.fill(WHITE) # 1. 배경을 먼저 흰색으로 칠함
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), radius) # 2. 새로운 위치에 원을 그림
    
    pygame.display.flip() # 3. 화면을 업데이트하여 보여줌
    clock.tick(60)       # 4. 초당 60프레임 유지

# 4. 종료 처리
pygame.quit()
sys.exit()