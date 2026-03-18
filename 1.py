import pygame
import sys
import random
import math

# 1. 초기화 및 설정
pygame.init()
pygame.font.init()

SW, SH = 800, 600
# 창 생성 직후 즉시 흰색으로 초기화 (반투명 현상 방지)
screen = pygame.display.set_mode((SW, SH))
screen.fill((255, 255, 255))
pygame.display.flip()

pygame.display.set_caption("Grow and Win! - Press R to Restart")

# 색상 및 폰트 설정
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 204, 0)
BLACK = (0, 0, 0)

font_large = pygame.font.SysFont("arial", 70, bold=True)
font_small = pygame.font.SysFont("arial", 25)

# 2. 게임 상태 초기화 함수
def reset_game():
    global p1_x, p1_y, p1_radius, p1_score
    global p2_x, p2_y, p2_radius, p2_score
    global item_x, item_y, game_over

    # 플레이어 1 초기화
    p1_x, p1_y = 600, 300
    p1_radius = 20
    p1_score = 0

    # 플레이어 2 초기화
    p2_x, p2_y = 200, 300
    p2_radius = 20
    p2_score = 0

    # 아이템 위치 초기화
    item_x = random.randint(20, SW - 20)
    item_y = random.randint(20, SH - 20)

    game_over = False

# 충돌 확인 함수
def is_colliding(x1, y1, r1, x2, y2, r2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance < (r1 + r2)

# 화면 중앙 글씨 출력 함수
def draw_center_text(text, font, color, y_offset=0):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(SW // 2, SH // 2 + y_offset))
    screen.blit(text_obj, text_rect)

# 게임 시작 전 첫 초기화
reset_game()
speed = 7
clock = pygame.time.Clock()
running = True

# 3. 메인 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 게임 종료 상태에서 키 이벤트 처리
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                reset_game() # R 키를 누르면 게임 리셋

    if not game_over:
        keys = pygame.key.get_pressed()
        # P1 조작 (화살표)
        if keys[pygame.K_LEFT]:  p1_x -= speed
        if keys[pygame.K_RIGHT]: p1_x += speed
        if keys[pygame.K_UP]:    p1_y -= speed
        if keys[pygame.K_DOWN]:  p1_y += speed
        # P2 조작 (WASD)
        if keys[pygame.K_a]:     p2_x -= speed
        if keys[pygame.K_d]:     p2_x += speed
        if keys[pygame.K_w]:     p2_y -= speed
        if keys[pygame.K_s]:     p2_y += speed

        # 화면 루핑 (P1)
        if p1_x > SW + p1_radius: p1_x = -p1_radius
        elif p1_x < -p1_radius: p1_x = SW + p1_radius
        if p1_y > SH + p1_radius: p1_y = -p1_radius
        elif p1_y < -p1_radius: p1_y = SH + p1_radius
        # 화면 루핑 (P2)
        if p2_x > SW + p2_radius: p2_x = -p2_radius
        elif p2_x < -p2_radius: p2_x = SW + p2_radius
        if p2_y > SH + p2_radius: p2_y = -p2_radius
        elif p2_y < -p2_radius: p2_y = SH + p2_radius

        # 아이템 충돌 체크
        item_r = 15
        if is_colliding(p1_x, p1_y, p1_radius, item_x, item_y, item_r):
            p1_score += 1
            p1_radius += 8
            item_x, item_y = random.randint(20, SW-20), random.randint(20, SH-20)
        
        if is_colliding(p2_x, p2_y, p2_radius, item_x, item_y, item_r):
            p2_score += 1
            p2_radius += 8
            item_x, item_y = random.randint(20, SW-20), random.randint(20, SH-20)

        if p1_score >= 5 or p2_score >= 5:
            game_over = True

    # 4. 그리기 영역
    screen.fill(WHITE)
    
    if not game_over:
        pygame.draw.circle(screen, YELLOW, (item_x, item_y), 15)
        # 점수 표시
        score_text = font_small.render(f"P1: {p1_score}  |  P2: {p2_score}", True, BLACK)
        screen.blit(score_text, (20, 20))

    pygame.draw.circle(screen, BLUE, (int(p1_x), int(p1_y)), p1_radius)
    pygame.draw.circle(screen, RED, (int(p2_x), int(p2_y)), p2_radius)

    if game_over:
        winner = "PLAYER 1" if p1_score >= 5 else "PLAYER 2"
        color = BLUE if p1_score >= 5 else RED
        draw_center_text(f"{winner} WINS!", font_large, color, -30)
        draw_center_text("Press 'R' to Restart or Close Window to Exit", font_small, BLACK, 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()