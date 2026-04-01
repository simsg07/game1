import pygame
import random
import sys
import math

# --- 초기화 ---
pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "nanumgothic", "dotum", "apple ghtic", "arial"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

# --- 설정 및 색상 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
RED, GREEN, BLUE = (255, 50, 50), (50, 255, 80), (50, 150, 255)
YELLOW, GOLD, PURPLE, ORANGE = (255, 255, 0), (255, 215, 0), (160, 32, 240), (255, 140, 0)
SKY_BLUE = (135, 206, 235)
DAY_BG, NIGHT_BG = (45, 55, 75), (15, 10, 25)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("보스 처치 보상 강화 (Q:종료, R:재시작)")
clock = pygame.time.Clock()
font_sm = get_korean_font(20)
font_md = get_korean_font(30)
font_lg = get_korean_font(60)

# --- 유틸리티 ---
def check_collision(pos, radius, rect):
    closest_x = max(rect.left, min(pos[0], rect.right))
    closest_y = max(rect.top, min(pos[1], rect.bottom))
    return ((pos[0] - closest_x)**2 + (pos[1] - closest_y)**2) < (radius**2)

class Enemy:
    def __init__(self, level):
        side = random.randint(0, 3)
        if side == 0: self.rect = pygame.Rect(random.randint(0, WIDTH), 10, 28, 28)
        elif side == 1: self.rect = pygame.Rect(random.randint(0, WIDTH), HEIGHT-40, 28, 28)
        elif side == 2: self.rect = pygame.Rect(10, random.randint(0, HEIGHT), 28, 28)
        else: self.rect = pygame.Rect(WIDTH-40, random.randint(0, HEIGHT), 28, 28)
        
        rand_val = random.random()
        if rand_val < 0.8: self.type = "basic"
        elif rand_val < 0.9: self.type = "ranger"
        else: self.type = "dasher"
            
        self.hp = 40 + level * 20
        self.speed = random.uniform(2.0, 3.2)
        self.timer = 0
        self.dash_vec = [0, 0]

    def update(self, p_pos, e_bullets):
        dx, dy = p_pos[0] - self.rect.centerx, p_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        
        if self.type == "basic":
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
        elif self.type == "ranger":
            if dist > 220:
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
            elif dist < 120:
                self.rect.x -= (dx / dist) * self.speed
                self.rect.y -= (dy / dist) * self.speed
            self.timer += 1
            if self.timer > 100:
                e_bullets.append({"pos": list(self.rect.center), "vel": [(dx/dist)*5, (dy/dist)*5]})
                self.timer = 0
        elif self.type == "dasher":
            self.timer += 1
            if self.timer < 70:
                self.rect.x += (dx / dist) * 1.5
                self.rect.y += (dy / dist) * 1.5
                self.dash_vec = [(dx/dist)*11, (dy/dist)*11]
            elif self.timer < 90:
                self.rect.x += self.dash_vec[0]
                self.rect.y += self.dash_vec[1]
            else: self.timer = 0

class Boss:
    def __init__(self, count):
        self.is_final = (count >= 3)
        size = 180 if self.is_final else 130
        self.rect = pygame.Rect(WIDTH//2 - size//2, -200, size, size)
        self.max_hp = 5000 * (2.8 ** count) if not self.is_final else 250000
        self.hp = self.max_hp
        self.entry = False
        self.timer, self.ang = 0, 0

    def update(self, p_pos, e_bullets):
        if not self.entry:
            self.rect.y += 3
            if self.rect.y >= 90: self.entry = True
            return
        self.rect.x += math.sin(pygame.time.get_ticks()*0.004) * 5
        self.timer += 1
        div = 6 if self.is_final else 15
        if self.timer % div == 0:
            count = 15 if self.is_final else 8
            for i in range(count):
                rad = math.radians(i * (360/count) + self.ang)
                e_bullets.append({"pos": list(self.rect.center), "vel": [math.cos(rad)*7, math.sin(rad)*7]})
            self.ang += 12

def main():
    while True:
        if not run_game(): break

def run_game():
    # 게임 상태 변수
    p_pos = [WIDTH//2, HEIGHT//2]
    p_radius, lives, level, exp, exp_next = 18, 3, 1, 0, 150
    dmg, atk_spd = 65, 1.0
    pierce_count = 1  # 탄환 관통 횟수
    
    boss_killed, cycle_timer, invinc = 0, 0, 0
    is_night, victory = False, False
    
    is_rolling, roll_timer, roll_cd, roll_ghosts = False, 0, 0, []
    enemies, bullets, e_bullets = [], [], []
    boss = None
    shoot_tick = 0

    def show_boss_reward():
        nonlocal dmg, atk_spd, pierce_count, lives
        waiting = True
        while waiting:
            screen.fill(BLACK)
            pygame.draw.rect(screen, GOLD, (50, 50, WIDTH-100, HEIGHT-100), 5)
            draw_center("◈ 보스 처치 특별 보상 ◈", 120, font_lg, GOLD)
            draw_center("강력한 유물 중 하나를 선택하세요", 220, font_sm, WHITE)
            draw_center("1. 전설의 칼날 (공격력 +150)", 320, font_md, RED)
            draw_center("2. 신속의 장화 (연사속도 +100%)", 380, font_md, BLUE)
            draw_center("3. 관통의 화살 (관통 횟수 +2)", 440, font_md, GREEN)
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_1: dmg += 150; waiting = False
                    if ev.key == pygame.K_2: atk_spd += 1.0; waiting = False
                    if ev.key == pygame.K_3: pierce_count += 2; waiting = False
                    if ev.key == pygame.K_q: pygame.quit(); sys.exit()

    running = True
    while running:
        clock.tick(FPS)
        cycle_timer += 1
        screen.fill(NIGHT_BG if is_night else DAY_BG)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: pygame.quit(); sys.exit()
                if e.key == pygame.K_r: return True

        # 낮/밤 전환
        if cycle_timer > 1800:
            is_night = not is_night
            cycle_timer = 0
            if is_night: boss = Boss(boss_killed)
            else: boss = None; e_bullets.clear()

        # 플레이어 이동
        keys = pygame.key.get_pressed()
        move_dir = [keys[pygame.K_RIGHT]-keys[pygame.K_LEFT], keys[pygame.K_DOWN]-keys[pygame.K_UP]]
        
        if keys[pygame.K_LSHIFT] and not is_rolling and roll_cd <= 0 and any(move_dir):
            is_rolling, roll_timer, roll_cd, invinc = True, 15, 45, 15
            roll_dir = move_dir

        if is_rolling:
            p_pos[0] += roll_dir[0] * 12
            p_pos[1] += roll_dir[1] * 12
            roll_timer -= 1
            if cycle_timer % 2 == 0: roll_ghosts.append([list(p_pos), 20])
            if roll_timer <= 0: is_rolling = False
        else:
            p_pos[0] += move_dir[0] * 5
            p_pos[1] += move_dir[1] * 5
            if roll_cd > 0: roll_cd -= 1

        p_pos[0] = max(p_radius, min(WIDTH-p_radius, p_pos[0]))
        p_pos[1] = max(p_radius, min(HEIGHT-p_radius, p_pos[1]))

        # 자동 공격
        if shoot_tick > 0: shoot_tick -= 1
        if keys[pygame.K_SPACE] and shoot_tick <= 0:
            targets = enemies + ([boss] if boss else [])
            if targets:
                target = min(targets, key=lambda t: math.hypot(p_pos[0]-t.rect.centerx, p_pos[1]-t.rect.centery))
                dx, dy = target.rect.centerx-p_pos[0], target.rect.centery-p_pos[1]
                dist = math.hypot(dx, dy) or 1
                bullets.append({"pos": list(p_pos), "vel": [(dx/dist)*16, (dy/dist)*16], "p": pierce_count, "hit_list": []})
                shoot_tick = int(20 / atk_spd)

        # 적 스폰
        if not is_night and random.random() < 0.07:
            enemies.append(Enemy(level))

        for en in enemies[:]:
            en.update(p_pos, e_bullets)
            if check_collision(p_pos, p_radius, en.rect) and invinc <= 0:
                lives -= 1; invinc = 60; enemies.remove(en)

        # 탄환 처리 (관통 로직 적용)
        for b in bullets[:]:
            b["pos"][0] += b["vel"][0]; b["pos"][1] += b["vel"][1]
            if b["pos"][0] < 0 or b["pos"][0] > WIDTH or b["pos"][1] < 0 or b["pos"][1] > HEIGHT:
                bullets.remove(b); continue

            # 보스 충돌
            if boss and boss.rect.collidepoint(b["pos"]) and boss not in b["hit_list"]:
                boss.hp -= dmg
                b["p"] -= 1
                b["hit_list"].append(boss)
                if boss.hp <= 0:
                    boss_killed += 1
                    victory = boss.is_final
                    if victory: running = False
                    else:
                        boss, is_night, cycle_timer = None, False, 0
                        show_boss_reward() # 보스 보상 창 띄우기
                if b["p"] <= 0: bullets.remove(b); continue
            
            # 잡몹 충돌
            for en in enemies[:]:
                if en.rect.collidepoint(b["pos"]) and en not in b["hit_list"]:
                    en.hp -= dmg
                    b["p"] -= 1
                    b["hit_list"].append(en)
                    if en.hp <= 0: enemies.remove(en); exp += 80
                    if b["p"] <= 0: 
                        if b in bullets: bullets.remove(b)
                        break

        if boss:
            boss.update(p_pos, e_bullets)
            if check_collision(p_pos, p_radius, boss.rect) and invinc <= 0:
                lives -= 1; invinc = 70
        for eb in e_bullets[:]:
            eb["pos"][0] += eb["vel"][0]; eb["pos"][1] += eb["vel"][1]
            if math.hypot(p_pos[0]-eb["pos"][0], p_pos[1]-eb["pos"][1]) < p_radius + 6:
                if invinc <= 0: lives -= 1; invinc = 70
                e_bullets.remove(eb)

        # 일반 레벨업
        if exp >= exp_next:
            level += 1; exp, exp_next = 0, int(exp_next*1.5)
            screen.fill(BLACK)
            draw_center("--- 레벨 업! ---", 150, font_lg, YELLOW)
            draw_center("1.공격력(+50) 2.연사속도(+35%) 3.체력회복", 350, font_md, WHITE)
            pygame.display.flip()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_1: dmg += 50; waiting = False
                        if ev.key == pygame.K_2: atk_spd += 0.35; waiting = False
                        if ev.key == pygame.K_3: lives = min(3, lives+1); waiting = False
                        if ev.key == pygame.K_q: pygame.quit(); sys.exit()

        if invinc > 0: invinc -= 1
        if lives <= 0: running = False

        # 그리기
        for g in roll_ghosts[:]:
            pygame.draw.circle(screen, (100, 150, 255), (int(g[0][0]), int(g[0][1])), p_radius, 1)
            g[1] -= 2
            if g[1] <= 0: roll_ghosts.remove(g)
        
        p_color = BLUE if invinc % 12 < 6 else WHITE
        pygame.draw.circle(screen, p_color, (int(p_pos[0]), int(p_pos[1])), p_radius)
        for en in enemies:
            ec = RED if en.type=="basic" else (GREEN if en.type=="ranger" else ORANGE)
            pygame.draw.rect(screen, ec, en.rect)
        for b in bullets:
            pygame.draw.circle(screen, SKY_BLUE if b["p"] > 0 else WHITE, (int(b["pos"][0]), int(b["pos"][1])), 5)
        for eb in e_bullets: pygame.draw.circle(screen, RED, (int(eb["pos"][0]), int(eb["pos"][1])), 6)
        
        if boss:
            b_color = GOLD if boss.is_final else PURPLE
            pygame.draw.rect(screen, b_color, boss.rect)
            pygame.draw.rect(screen, RED, (WIDTH//2-150, 20, (max(0, boss.hp)/boss.max_hp)*300, 15))

        # UI
        mode_txt = "밤 (보스전)" if is_night else f"낮 (다음 밤까지 {(1800-cycle_timer)//60}초)"
        screen.blit(font_sm.render(mode_txt, True, YELLOW), (20, 20))
        screen.blit(font_sm.render(f"레벨: {level}  관통: {pierce_count}  체력: ", True, WHITE), (20, 50))
        screen.blit(font_sm.render("♥" * lives, True, RED), (230, 50))
        screen.blit(font_sm.render(f"보스 처치: {boss_killed}/3 | Q:종료 R:재시작", True, WHITE), (20, 80))
        pygame.draw.rect(screen, GREEN, (0, HEIGHT-10, (exp/exp_next)*WIDTH, 10))
        pygame.display.flip()

    screen.fill(BLACK)
    draw_center("★ 승 리 ★" if victory else "게임 오버", HEIGHT//2-50, font_lg, GOLD if victory else RED)
    draw_center("Q: 종료 | R: 다시 시작", HEIGHT//2 + 50, font_md, WHITE)
    pygame.display.flip()
    
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q: pygame.quit(); sys.exit()
                if ev.key == pygame.K_r: return True

def draw_center(txt, y, font, color):
    s = font.render(txt, True, color)
    screen.blit(s, (WIDTH//2 - s.get_width()//2, y))

if __name__ == "__main__":
    main()