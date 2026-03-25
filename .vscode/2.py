import pygame
import math
from sprites import load_sprite

# 1. 초기화 및 창 설정
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Collision Lab: Fixed Movement")

# --- 설정 및 색상 ---
COLOR_BG, COLOR_GRID = (15, 20, 25), (30, 40, 50)
COLOR_OBB, COLOR_AABB, COLOR_CIRCLE = (0, 255, 150), (255, 50, 50), (50, 150, 255)
COLOR_HIT_BG, COLOR_TEXT = (80, 0, 0), (200, 200, 200)
font_ui = pygame.font.SysFont("consolas", 16)

# 2. SAT 충돌 관련 함수 (기존과 동일)
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

# 3. 스프라이트 및 초기 변수
sprite_names = ["rocket", "adventurer", "stone", "sword"]
current_idx = 0

def get_current_assets(idx):
    name = sprite_names[idx]
    s_size = (120, 120) if name in ["stone", "sword"] else (100, 150)
    p_size = (80, 80) if name in ["stone", "sword"] else (60, 90)
    return load_sprite(name, s_size), load_sprite(name, p_size)

static_img, player_img = get_current_assets(current_idx)
static_pos = pygame.Vector2(400, 300)
player_pos = pygame.Vector2(150, 150)
angle = 0
player_speed = 300  # 초당 이동 픽셀 (프레임 독립적)

# 4. 메인 루프
running = True
clock = pygame.time.Clock()

while running:
    # 델타 타임 계산 (초 단위)
    dt = clock.tick(60) / 1000.0

    # 이벤트 처리 (토글 방식 수정)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                current_idx = (current_idx + 1) % len(sprite_names)
                static_img, player_img = get_current_assets(current_idx)

    # 이동 처리 (정규화된 벡터 이동)
    keys = pygame.key.get_pressed()
    move_vec = pygame.Vector2(0, 0)
    if keys[pygame.K_LEFT]:  move_vec.x -= 1
    if keys[pygame.K_RIGHT]: move_vec.x += 1
    if keys[pygame.K_UP]:    move_vec.y -= 1
    if keys[pygame.K_DOWN]:  move_vec.y += 1

    # 대각선 속도 보정 (버니합 방지 핵심)
    if move_vec.length() > 0:
        move_vec = move_vec.normalize()
        player_pos += move_vec * player_speed * dt

    # 회전 로직
    angle += (300 * dt if keys[pygame.K_z] else 60 * dt)

    # --- 이하 렌더링 및 충돌 판정 로직 (동일) ---
    s_w, s_h = static_img.get_size()
    p_w, p_h = player_img.get_size()
    static_vertices = get_rotated_vertices(static_pos, s_w, s_h, angle)
    player_vertices = get_rotated_vertices(player_pos, p_w, p_h, 0)
    rotated_static = pygame.transform.rotate(static_img, angle)
    static_aabb = rotated_static.get_rect(center=static_pos)
    player_aabb = player_img.get_rect(center=player_pos)
    s_rad, p_rad = max(s_w, s_h)/2, max(p_w, p_h)/2
    circle_hit = static_pos.distance_to(player_pos) < (s_rad + p_rad)
    aabb_hit = player_aabb.colliderect(static_aabb)
    obb_hit = check_sat_collision(static_vertices, player_vertices)

    screen.fill(COLOR_HIT_BG if obb_hit else COLOR_BG)
    for i in range(0, 800, 40): pygame.draw.line(screen, COLOR_GRID, (i, 0), (i, 600))
    for i in range(0, 600, 40): pygame.draw.line(screen, COLOR_GRID, (0, i), (800, i))
    screen.blit(rotated_static, static_aabb)
    screen.blit(player_img, player_aabb)
    pygame.draw.circle(screen, COLOR_CIRCLE, (int(static_pos.x), int(static_pos.y)), int(s_rad), 1)
    pygame.draw.rect(screen, COLOR_AABB, static_aabb, 1)
    pygame.draw.polygon(screen, COLOR_OBB, static_vertices, 2)
    pygame.draw.polygon(screen, COLOR_OBB, player_vertices, 2)

    status = [f"MODE: {sprite_names[current_idx].upper()}",
              f"CIRCLE: {'DETECT' if circle_hit else 'SAFE'}",
              f"AABB:   {'DETECT' if aabb_hit else 'SAFE'}",
              f"OBB:    {'DETECT' if obb_hit else 'SAFE'}"]
    for i, text in enumerate(status):
        screen.blit(font_ui.render(text, True, COLOR_TEXT), (20, 20 + i * 25))
    screen.blit(font_ui.render("Press 'X' to Switch / 'Z' to Turbo Rotate", True, (200, 200, 100)), (20, 570))

    pygame.display.flip()

pygame.quit()