import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Fancy Particle Playground")

clock = pygame.time.Clock()

particles = []

# --- 글로우(빛무리) 효과를 위한 표면(Surface) 캐싱 ---
# 매 프레임마다 그라데이션을 그리면 느려지므로, 한 번 만든 빛무리는 저장해두고 재사용합니다.
glow_cache = {}

def get_glow_surface(radius, color):
    radius = int(radius)
    if radius <= 0:
        return None
        
    key = (radius, color)
    if key not in glow_cache:
        # 투명도를 지원하는 빈 Surface 생성
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # 여러 겹의 반투명한 원을 그려 그라데이션(빛) 효과 생성
        for r in range(radius, 0, -1):
            alpha = int(255 * ((radius - r) / radius) ** 1.5) # 부드러운 퍼짐
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        glow_cache[key] = surf
        
    return glow_cache[key]

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # 폭죽처럼 사방으로 퍼지도록 각도와 속도 설정
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 10) # 속도를 높여 더 화려하게

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.max_life = random.randint(40, 100)
        self.life = self.max_life
        self.base_size = random.uniform(10, 25) # 크기도 조금 더 크게

        # 화려한 네온 컬러 팔레트 (시안, 마젠타, 옐로우, 라임 등)
        self.color = random.choice([
            (0, 255, 255),   # Cyan
            (255, 0, 255),   # Magenta
            (150, 0, 255),   # Purple
            (0, 150, 255),   # Deep Blue
            (255, 255, 0),   # Yellow
            (50, 255, 50)    # Lime Green
        ])

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # 물리 효과: 마찰력(Friction)과 중력(Gravity)
        self.vx *= 0.94  # 공기 저항 (속도가 점점 줄어듦)
        self.vy *= 0.94
        self.vy += 0.15  # 중력 (아래로 떨어짐)

        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            # 수명에 따라 크기가 점점 줄어드는 비율 계산
            ratio = self.life / self.max_life
            current_size = self.base_size * ratio
            
            glow_surf = get_glow_surface(current_size, self.color)
            if glow_surf:
                # 중심점 위치 조정 후 화면에 그리기
                # BLEND_RGB_ADD 플래그를 사용하여 색상이 겹칠수록 밝아지는 빛 효과 연출
                rect = glow_surf.get_rect(center=(int(self.x), int(self.y)))
                surf.blit(glow_surf, rect, special_flags=pygame.BLEND_RGB_ADD)
                
            # 중심부에 밝은 흰색 코어를 그려 더 빛나 보이게 함
            core_size = max(1, int(current_size * 0.2))
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), core_size)

    def alive(self):
        return self.life > 0

def draw_background(surface, t):
    # 파티클의 네온 빛이 돋보이도록 어둡고 몽환적인 배경 설정
    surface.fill((10, 12, 20))
    
    # 은은하게 움직이는 배경 선 (선택 사항)
    for y in range(0, HEIGHT, 40):
        offset = math.sin(y * 0.02 + t) * 20
        pygame.draw.line(surface, (20, 25, 35), (0, y + offset), (WIDTH, y + offset), 1)

running = True
time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    # 마우스를 클릭하고 있을 때 파티클 대량 생성
    if buttons[0]:
        for _ in range(12): # 생성 개수를 늘림
            # 마우스 위치에서 약간 분산시켜 생성
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            particles.append(Particle(mouse_x + offset_x, mouse_y + offset_y))

    time += 0.05

    draw_background(screen, time)

    for p in particles:
        p.update()
        p.draw(screen)

    # 살아있는 파티클만 리스트에 남김
    particles = [p for p in particles if p.alive()]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()