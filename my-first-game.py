import pygame
import random
import math

# 초기화
pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Neon Fireworks - Fixed Background")

clock = pygame.time.Clock()

# 잔상을 위한 별도의 Surface (RGBA 지원)
# 이 표면이 파티클의 궤적을 기억합니다.
trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

particles = []
glow_cache = {}

def get_glow_surface(radius, color):
    radius = int(radius)
    if radius <= 0: return None
    key = (radius, color)
    if key not in glow_cache:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(150 * ((radius - r) / radius) ** 2)
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        glow_cache[key] = surf
    return glow_cache[key]

class Particle:
    def __init__(self, x, y, is_explosion=False):
        self.x = x
        self.y = y
        self.hue = random.random()
        
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 12) if is_explosion else random.uniform(1, 5)
        
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.max_life = random.randint(30, 80)
        self.life = self.max_life
        self.base_size = random.uniform(8, 20)

    def update(self):
        self.vx *= 0.96
        self.vy *= 0.96
        self.vy += 0.12 
        self.x += self.vx
        self.y += self.vy
        self.hue += 0.01
        if self.hue > 1.0: self.hue = 0
        self.life -= 1

    def get_current_color(self):
        c = pygame.Color(0)
        c.hsva = (self.hue * 360, 90, 100, 100)
        return (c.r, c.g, c.b)

    def draw(self, surf):
        ratio = self.life / self.max_life
        size = self.base_size * ratio * random.uniform(0.7, 1.3)
        color = self.get_current_color()
        
        glow_surf = get_glow_surface(size, color)
        if glow_surf:
            rect = glow_surf.get_rect(center=(int(self.x), int(self.y)))
            # 잔상 레이어(trail_surf)에 빛무리를 그립니다.
            surf.blit(glow_surf, rect, special_flags=pygame.BLEND_RGBA_ADD)
            
            # 메인 화면(screen)에는 파티클의 중심(코어)을 그려서 선명함을 유지합니다.
            core_size = max(1, int(size * 0.3))
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), core_size)

running = True
while running:
    # 1. 배경색 고정 (매 프레임 완전히 새로 칠함)
    screen.fill((10, 10, 25))

    # 2. 잔상 서서히 지우기 (배경색에는 영향을 주지 않고 trail_surf의 알파값만 깎음)
    # 마지막 숫자가 클수록 잔상이 짧아집니다 (현재 25)
    fade_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surf.fill((0, 0, 0, 25)) 
    trail_surf.blit(fade_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for _ in range(50):
                particles.append(Particle(*event.pos, is_explosion=True))

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        for _ in range(5):
            particles.append(Particle(mx, my))

    # 3. 파티클 업데이트 및 잔상 레이어에 그리기
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)
        else:
            p.draw(trail_surf)

    # 4. 최종적으로 잔상 레이어를 화면에 덮어씌움
    screen.blit(trail_surf, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()