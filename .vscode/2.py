import pygame
import math
from sprites import load_sprite  # sprites.py에서 함수 임포트

# 1. 초기화 및 창 설정
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sprite Collision Lab: Circle/AABB/OBB")

# --- 설정 및 색상 ---
COLOR_BG, COLOR_GRID = (15, 20, 25), (30, 40, 50)
COLOR_OBB, COLOR_AABB, COLOR_CIRCLE = (0, 255, 150), (255, 50, 50), (50, 150, 255)
COLOR_HIT_BG, COLOR_TEXT = (80, 0, 0), (200, 200, 200)
font_ui = pygame.font.SysFont("consolas", 16)

# 2. SAT 충돌 관련 함수
def get_rotated_vertices(center, width, height, angle):
    rad = math.radians(-angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    hw, hh = width / 2, height / 2
    points = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    return [pygame.Vector2(center.x + px*cos_a - py*sin_a, center.y + px*sin_a + py*cos_a) for px, py in points]

def check_sat_collision(pts1, pts2):
    def get_axes(pts):
        axes = []
        for i in range(len(pts)):
            edge = pts[(i+1)%len(pts)] - pts[i]
            if edge.length() != 0: axes.append(pygame.Vector2(-edge.y, edge.x).normalize())
        return axes
    axes = get_axes(pts1) + get_axes(pts2)
    for axis in axes:
        dots1, dots2 = [p.dot(axis) for p in pts1], [p.dot(axis) for p in pts2]
        if max(dots1) < min(dots2) or max(dots2) < min(dots1): return False
    return True

# 3. 스프라이트 관리 로직
sprite_names = ["rocket", "adventurer", "stone", "sword"]
current_idx = 0

def get_current_assets(idx):
    name = sprite_names[idx]
    # 이미지별 적절한 크기 설정 (원하는 대로 조절 가능)
    s_size = (120, 120) if name in ["stone", "sword"] else (100, 150)
    p_size = (80, 80) if name in ["stone", "sword"] else (60, 90)
    return load_sprite(name, s_size), load_sprite(name, p_size)

static_img, player_img = get_current_assets(current_idx)
static_pos = pygame.Vector2(400, 300)
player_pos = pygame.Vector2(150, 150)
angle = 0
player_speed = 5
x_key_pressed = False

# 4. 메인 루프
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # 입력 처리: X 키로 스프라이트 체인지
    keys = pygame.key.get_pressed()
    if keys[pygame.K_x] and not x_key_pressed:
        current_idx = (current_idx + 1) % len(sprite_names)
        static_img, player_img = get_current_assets(current_idx)
        x_key_pressed = True
    elif not keys[pygame.K_x]: x_key_pressed = False

    # 플레이어 이동 및 회전
    if keys[pygame.K_LEFT]: player_pos.x -= player_speed
    if keys[pygame.K_RIGHT]: player_pos.x += player_speed
    if keys[pygame.K_UP]: player_pos.y -= player_speed
    if keys[pygame.K_DOWN]: player_pos.y += player_speed
    angle += (5 if keys[pygame.K_z] else 1)

    # 히트박스 데이터 업데이트
    s_w, s_h = static_img.get_size()
    p_w, p_h = player_img.get_size()
    
    static_vertices = get_rotated_vertices(static_pos, s_w, s_h, angle)
    player_vertices = get_rotated_vertices(player_pos, p_w, p_h, 0)

    # 이미지 회전을 반영한 Rect(AABB) 계산
    rotated_static = pygame.transform.rotate(static_img, angle)
    static_aabb = rotated_static.get_rect(center=static_pos)
    player_aabb = player_img.get_rect(center=player_pos)

    # 충돌 판정
    s_rad, p_rad = max(s_w, s_h)/2, max(p_w, p_h)/2
    circle_hit = static_pos.distance_to(player_pos) < (s_rad + p_rad)
    aabb_hit = player_aabb.colliderect(static_aabb)
    obb_hit = check_sat_collision(static_vertices, player_vertices)

    # 그리기 영역
    screen.fill(COLOR_HIT_BG if obb_hit else COLOR_BG)
    
    # 그리드
    for i in range(0, 800, 40): pygame.draw.line(screen, COLOR_GRID, (i, 0), (i, 600))
    for i in range(0, 600, 40): pygame.draw.line(screen, COLOR_GRID, (0, i), (800, i))

    # 본체 출력
    screen.blit(rotated_static, static_aabb)
    screen.blit(player_img, player_aabb)

    # 디버그용 히트박스 시각화
    pygame.draw.circle(screen, COLOR_CIRCLE, (int(static_pos.x), int(static_pos.y)), int(s_rad), 1)
    pygame.draw.rect(screen, COLOR_AABB, static_aabb, 1)
    pygame.draw.polygon(screen, COLOR_OBB, static_vertices, 2)
    pygame.draw.polygon(screen, COLOR_OBB, player_vertices, 2)

    # UI 정보창
    ui_box = pygame.Surface((240, 130), pygame.SRCALPHA)
    ui_box.fill((0, 0, 0, 150))
    screen.blit(ui_box, (10, 10))
    
    status = [
        f"MODE: {sprite_names[current_idx].upper()}",
        f"CIRCLE: {'DETECT' if circle_hit else 'SAFE'}",
        f"AABB:   {'DETECT' if aabb_hit else 'SAFE'}",
        f"OBB:    {'DETECT' if obb_hit else 'SAFE'}"
    ]
    for i, text in enumerate(status):
        screen.blit(font_ui.render(text, True, COLOR_TEXT), (20, 20 + i * 25))

    screen.blit(font_ui.render("Press 'X' to Switch / 'Z' to Turbo Rotate", True, (200, 200, 100)), (20, 570))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()