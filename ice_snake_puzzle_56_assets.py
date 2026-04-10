import os
import sys
import pygame

pygame.init()

CELL = 64
SPRITE_SIZE = 56
COLS, ROWS = 16, 12
HUD_HEIGHT = 64
BOTTOM_HINT_HEIGHT = 44
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
SCREEN_HEIGHT = HEIGHT + HUD_HEIGHT
FPS = 60

WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
DARK_GRAY = (45, 45, 45)
ICE = (180, 230, 255)
ICE_LINE = (210, 245, 255)
PLAYER_HEAD = (40, 120, 255)
PLAYER_BODY = (120, 185, 255)
WALL = (50, 50, 50)
ROCK = (120, 120, 120)
EXIT_CLOSED = (120, 140, 220)
EXIT_OPEN = (70, 200, 120)
TEXT = (250, 250, 250)
RED = (220, 70, 70)
GREEN = (70, 220, 120)
BLUE = (90, 170, 255)
PURPLE = (140, 110, 220)
KEY_GOLD = (245, 200, 40)
KEY_SHADOW = (170, 120, 20)

screen = pygame.display.set_mode((WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ice Snake Puzzle")
clock = pygame.time.Clock()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", "arial"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

font_sm = get_korean_font(22)
font_md = get_korean_font(34)
font_lg = get_korean_font(54)

SPRITES_DIR = os.path.join(os.path.dirname(__file__), "sprites")
ASSET_FILES = {
    "ice": "ice.png",
    "wall": "wall.png",
    "rock": "rock.png",
    "portal_closed": "portal_closed.png",
    "portal_open": "portal_open.png",
    "spike": "spike.png",
    "key": "key.png",
}

def safe_load_image(path, size=(SPRITE_SIZE, SPRITE_SIZE)):
    try:
        img = pygame.image.load(path).convert_alpha()
        if img.get_size() != size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

def load_assets():
    assets = {}
    for key, filename in ASSET_FILES.items():
        assets[key] = safe_load_image(os.path.join(SPRITES_DIR, filename))
    return assets

ASSETS = load_assets()

TUTORIAL_LEVELS = [
    {
        "name": "튜토리얼 1",
        "hint": "방향키를 누르면 벽이나 바위 전까지 미끄러집니다.",
        "map": [
            "################",
            "#.............E#",
            "#..............#",
            "#..............#",
            "#..............#",
            "#......P.......#",
            "#..............#",
            "#..............#",
            "#..............#",
            "#......R.......#",
            "#..............#",
            "################",
        ],
    },
    {
        "name": "튜토리얼 2",
        "hint": "열쇠를 먼저 먹어야 출구가 열립니다.",
        "map": [
            "################",
            "#............E.#",
            "#..............#",
            "#....#####.....#",
            "#..............#",
            "#......P.......#",
            "#..............#",
            "#.....#####....#",
            "#..............#",
            "#.......K......#",
            "#..............#",
            "################",
        ],
    },
    {
        "name": "튜토리얼 3",
        "hint": "자기 몸에 닿으면 죽습니다. 경로를 설계하세요.",
        "map": [
            "################",
            "#.............E#",
            "#..............#",
            "#...R......R...#",
            "#..............#",
            "#......P.......#",
            "#..............#",
            "#...R......R...#",
            "#..............#",
            "#.......K......#",
            "#..............#",
            "################",
        ],
    },
]

LEVELS = [
    # 1
    [
        "################",
        "#........R.....#",
        "#.........E....#",
        "#..............#",
        "#..............#",
        "#......P.......#",
        "#..............#",
        "#..............#",
        "#..R...........#",
        "#......RK......#",
        "#..............#",
        "################",
    ],

    # 2
    [
        "################",
        "#.....R.R......#",
        "#.........R...E#",
        "#........R.....#",
        "#....R.........#",
        "#...RP.........#",
        "#..........R...#",
        "#..R...........#",
        "#......R.......#",
        "#..K...........#",
        "#.....R........#",
        "################",
    ],

    # 3
    [
        "################",
        "#..............#",
        "#......R....E..#",
        "#..............#",
        "#..............#",
        "#......P.......#",
        "#..............#",
        "#..............#",
        "#..............#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 4
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#..............#",
        "#....R.........#",
        "#......P.......#",
        "#..............#",
        "#.........R....#",
        "#..............#",
        "#..K...........#",
        "#..............#",
        "################",
    ],

    # 5
    [
        "################",
        "#..............#",
        "#....R......E..#",
        "#..............#",
        "#..............#",
        "#......P.......#",
        "#..............#",
        "#..............#",
        "#......R.......#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 6
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#....####......#",
        "#..............#",
        "#......P.......#",
        "#..............#",
        "#......####....#",
        "#..............#",
        "#..K...........#",
        "#..............#",
        "################",
    ],

    # 7
    [
        "################",
        "#..............#",
        "#......R....E..#",
        "#..............#",
        "#....####......#",
        "#......P.......#",
        "#..............#",
        "#......####....#",
        "#..............#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 8
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#..............#",
        "#....R.........#",
        "#......P.......#",
        "#.........R....#",
        "#..............#",
        "#..............#",
        "#..K...........#",
        "#..............#",
        "################",
    ],

    # 9
    [
        "################",
        "#..............#",
        "#....####...E..#",
        "#..............#",
        "#..............#",
        "#......P.......#",
        "#..............#",
        "#..............#",
        "#....####......#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 10
    [
        "################",
        "#..............#",
        "#......R....E..#",
        "#..............#",
        "#....####......#",
        "#......P.......#",
        "#..............#",
        "#......####....#",
        "#..............#",
        "#..K....R......#",
        "#..............#",
        "################",
    ],

    # 11
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#......#.......#",
        "#......#.......#",
        "#..P...#.......#",
        "#......#.......#",
        "#......#.......#",
        "#..............#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 12
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#......#.......#",
        "#......#.......#",
        "#..P...#.......#",
        "#......#.......#",
        "#......#.......#",
        "#..............#",
        "#..K...........#",
        "#..............#",
        "################",
    ],

    # 13
    [
        "################",
        "#..............#",
        "#....R......E..#",
        "#......#.......#",
        "#......#.......#",
        "#..P...#.......#",
        "#......#.......#",
        "#......#.......#",
        "#..............#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 14
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#....####......#",
        "#..............#",
        "#..P...........#",
        "#..............#",
        "#......R.......#",
        "#..............#",
        "#..K....####...#",
        "#..............#",
        "################",
    ],

    # 15
    [
        "################",
        "#..............#",
        "#......R....E..#",
        "#....####......#",
        "#..............#",
        "#..P...........#",
        "#..............#",
        "#......R.......#",
        "#..............#",
        "#..K....####...#",
        "#..............#",
        "################",
    ],

    # 16
    [
        "################",
        "#..............#",
        "#...........E.S#",
        "#......#.......#",
        "#......#.......#",
        "#..P...#.......#",
        "#......#.......#",
        "#......#.......#",
        "#..............#",
        "#..K...........#",
        "#..............#",
        "################",
    ],

    # 17
    [
        "################",
        "#..............#",
        "#....R......E.S#",
        "#......#.......#",
        "#......#.......#",
        "#..P...#.......#",
        "#......#.......#",
        "#......#.......#",
        "#..............#",
        "#.......K......#",
        "#..............#",
        "################",
    ],

    # 18
    [
        "################",
        "#..............#",
        "#...........E..#",
        "#....####......#",
        "#..............#",
        "#..P.....S.....#",
        "#..............#",
        "#......R.......#",
        "#..............#",
        "#..K....####...#",
        "#..............#",
        "################",
    ],

    # 19
    [
        "################",
        "#..............#",
        "#......R....E..#",
        "#....####......#",
        "#..............#",
        "#..P.....S.....#",
        "#..............#",
        "#......R.......#",
        "#..............#",
        "#..K....####...#",
        "#..............#",
        "################",
    ],

    # 20
    [
        "################",
        "#..............#",
        "#...........E.S#",
        "#......#.......#",
        "#..R...#.......#",
        "#..P...#.......#",
        "#......#...R...#",
        "#......#.......#",
        "#..............#",
        "#..K.......S...#",
        "#..............#",
        "################",
    ],
]

def grid_to_pixel(pos):
    x, y = pos
    return x * CELL, y * CELL + HUD_HEIGHT

def draw_text_center(text, y, font, color):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS

def center_blit(img, px, py):
    if img is None:
        return
    offset = (CELL - SPRITE_SIZE) // 2
    screen.blit(img, (px + offset, py + offset))

class Level:
    def __init__(self, raw_map):
        self.walls = set()
        self.rocks = set()
        self.spikes = set()
        self.key_pos = None
        self.exit_pos = None
        self.start_pos = None

        for y, row in enumerate(raw_map):
            for x, ch in enumerate(row):
                if ch == "#":
                    self.walls.add((x, y))
                elif ch == "R":
                    self.rocks.add((x, y))
                elif ch == "S":
                    self.spikes.add((x, y))
                elif ch == "K":
                    self.key_pos = (x, y)
                elif ch == "E":
                    self.exit_pos = (x, y)
                elif ch == "P":
                    self.start_pos = (x, y)

def load_level(idx, mode="stage"):
    if mode == "tutorial":
        level_data = TUTORIAL_LEVELS[idx]
        level = Level(level_data["map"])
        stage_name = level_data["name"]
        hint = level_data["hint"]
        total = len(TUTORIAL_LEVELS)
    else:
        level = Level(LEVELS[idx])
        stage_name = f"스테이지 {idx + 1}"
        if idx < 5:
            hint = "기본 규칙 구간"
        elif idx < 10:
            hint = "몸이 길어지는 경로를 읽는 구간"
        elif idx < 15:
            hint = "이동 순서와 정지 위치가 중요합니다"
        else:
            hint = "후반부: 가시와 좁은 경로를 함께 계산하세요"
        total = len(LEVELS)

    return {
        "mode": mode,
        "level_index": idx,
        "level_total": total,
        "stage_name": stage_name,
        "hint": hint,
        "level": level,
        "snake": [level.start_pos],
        "has_key": False,
        "state": "playing",
        "message": "",
    }

def slide_snake(game, direction):
    if game["state"] != "playing":
        return

    dx, dy = direction
    snake = game["snake"]
    level = game["level"]

    x, y = snake[0]
    trail = []
    moved = False

    while True:
        nx, ny = x + dx, y + dy

        if not in_bounds(nx, ny) or (nx, ny) in level.walls or (nx, ny) in level.rocks:
            break

        if (nx, ny) in snake or (nx, ny) in trail:
            game["state"] = "gameover"
            game["message"] = "자기 몸에 부딪혔습니다."
            return

        if (nx, ny) in level.spikes:
            game["state"] = "gameover"
            game["message"] = "가시에 닿았습니다."
            return

        x, y = nx, ny
        trail.append((x, y))
        moved = True

        if level.key_pos is not None and (x, y) == level.key_pos:
            game["has_key"] = True
            level.key_pos = None

        if (x, y) == level.exit_pos and game["has_key"]:
            if trail:
                game["snake"] = [trail[-1]] + trail[:-1][::-1] + snake
            game["state"] = "clear"
            game["message"] = "스테이지 클리어"
            return

    if moved:
        game["snake"] = [trail[-1]] + trail[:-1][::-1] + snake

def draw_ice_fallback(px, py):
    pygame.draw.rect(screen, ICE, (px, py, CELL, CELL))
    pygame.draw.rect(screen, ICE_LINE, (px, py, CELL, CELL), 1)

def draw_wall_fallback(px, py):
    pygame.draw.rect(screen, WALL, (px, py, CELL, CELL))

def draw_rock_fallback(px, py):
    pygame.draw.rect(screen, ROCK, (px + 8, py + 8, CELL - 16, CELL - 16), border_radius=12)

def draw_key(px, py):
    cx = px + CELL // 2
    cy = py + CELL // 2

    pygame.draw.circle(screen, KEY_GOLD, (cx - 10, cy - 2), 12, 5)
    pygame.draw.rect(screen, KEY_GOLD, (cx, cy - 5, 22, 10), border_radius=3)
    pygame.draw.rect(screen, KEY_GOLD, (cx + 14, cy - 5, 4, 16))
    pygame.draw.rect(screen, KEY_GOLD, (cx + 20, cy - 5, 4, 12))

    pygame.draw.circle(screen, KEY_SHADOW, (cx - 10, cy - 2), 12, 2)
    pygame.draw.rect(screen, KEY_SHADOW, (cx, cy - 5, 22, 10), 2, border_radius=3)

def draw_exit_fallback(px, py, opened):
    color = EXIT_OPEN if opened else EXIT_CLOSED
    pygame.draw.rect(screen, color, (px + 6, py + 6, CELL - 12, CELL - 12), border_radius=8)

def draw_spike_fallback(px, py):
    points = [
        (px + 10, py + CELL - 8),
        (px + 18, py + 26),
        (px + 28, py + CELL - 8),
        (px + 38, py + 18),
        (px + 48, py + CELL - 8),
        (px + 58, py + 22),
    ]
    pygame.draw.polygon(screen, PURPLE, points)

def draw_player(px, py, is_head):
    if is_head:
        pygame.draw.rect(screen, PLAYER_HEAD, (px + 10, py + 10, CELL - 20, CELL - 20), border_radius=10)
        pygame.draw.rect(screen, WHITE, (px + 16, py + 16, CELL - 32, CELL - 32), 2, border_radius=8)
    else:
        pygame.draw.rect(screen, PLAYER_BODY, (px + 18, py + 18, CELL - 36, CELL - 36), border_radius=8)

def draw_asset(name, pos, fallback_func=None, extra=None):
    px, py = grid_to_pixel(pos)
    img = ASSETS.get(name)

    if img is not None:
        center_blit(img, px, py)
    elif fallback_func:
        if extra is None:
            fallback_func(px, py)
        else:
            fallback_func(px, py, extra)

def draw_board(game):
    screen.fill(DARK_GRAY)
    level = game["level"]

    for y in range(ROWS):
        for x in range(COLS):
            draw_asset("ice", (x, y), draw_ice_fallback)

    for pos in level.walls:
        draw_asset("wall", pos, draw_wall_fallback)

    for pos in level.rocks:
        draw_asset("rock", pos, draw_rock_fallback)

    for pos in level.spikes:
        draw_asset("spike", pos, draw_spike_fallback)

    if level.key_pos is not None:
        if ASSETS["key"] is not None:
            draw_asset("key", level.key_pos)
        else:
            px, py = grid_to_pixel(level.key_pos)
            draw_key(px, py)

    if game["has_key"]:
        draw_asset("portal_open", level.exit_pos, draw_exit_fallback, True)
    else:
        draw_asset("portal_closed", level.exit_pos, draw_exit_fallback, False)

    snake = game["snake"]
    for seg in reversed(snake):
        px, py = grid_to_pixel(seg)
        draw_player(px, py, seg == snake[0])

    pygame.draw.rect(screen, (15, 15, 20), (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, (90, 90, 100), (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 2)

    if game["mode"] == "tutorial":
        left_text = f"{game['stage_name']} ({game['level_index'] + 1}/{game['level_total']})"
    else:
        left_text = f"Stage: {game['level_index'] + 1}/{game['level_total']}"

    key_text = "Key: O" if game["has_key"] else "Key: X"
    help_text = "방향키 이동   R 재시작   ESC 메뉴"

    screen.blit(font_sm.render(left_text, True, TEXT), (16, 18))
    screen.blit(font_sm.render(key_text, True, TEXT), (340, 18))
    screen.blit(font_sm.render(help_text, True, TEXT), (520, 18))

    if game["hint"]:
        hint_bg = pygame.Surface((WIDTH, BOTTOM_HINT_HEIGHT), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 100))
        screen.blit(hint_bg, (0, SCREEN_HEIGHT - BOTTOM_HINT_HEIGHT))
        screen.blit(font_sm.render(game["hint"], True, WHITE), (16, SCREEN_HEIGHT - 34))

def draw_overlay(game):
    if game["state"] == "gameover":
        overlay = pygame.Surface((WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))
        draw_text_center("GAME OVER", HUD_HEIGHT + 180, font_lg, RED)
        draw_text_center(game["message"], HUD_HEIGHT + 255, font_md, WHITE)
        draw_text_center("R: 재시작   ESC: 메뉴", HUD_HEIGHT + 320, font_md, WHITE)

    elif game["state"] == "clear":
        overlay = pygame.Surface((WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        draw_text_center("STAGE CLEAR", HUD_HEIGHT + 180, font_lg, GREEN)
        msg = "ENTER: 완료 화면" if game["level_index"] + 1 >= game["level_total"] else "ENTER: 다음 스테이지"
        draw_text_center(msg, HUD_HEIGHT + 255, font_md, WHITE)
        draw_text_center("R: 재시작   ESC: 메뉴", HUD_HEIGHT + 315, font_md, WHITE)

    elif game["state"] == "finish":
        overlay = pygame.Surface((WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title = "튜토리얼 완료" if game["mode"] == "tutorial" else "ALL CLEAR"
        color = BLUE if game["mode"] == "tutorial" else KEY_GOLD
        draw_text_center(title, HUD_HEIGHT + 180, font_lg, color)
        draw_text_center("ENTER: 메뉴로", HUD_HEIGHT + 255, font_md, WHITE)
        draw_text_center("R: 처음부터 다시", HUD_HEIGHT + 315, font_md, WHITE)

def draw_menu():
    screen.fill(DARK_GRAY)
    draw_text_center("ICE SNAKE PUZZLE", 120, font_lg, BLUE)
    draw_text_center("1. 게임 시작", 260, font_md, WHITE)
    draw_text_center("2. 튜토리얼", 320, font_md, WHITE)
    draw_text_center("Q. 종료", 380, font_md, WHITE)
    draw_text_center("플레이어는 파란 네모로 표시됩니다.", 500, font_sm, WHITE)
    draw_text_center("sprites 폴더에 개별 png를 넣으면 자동 적용됩니다.", 540, font_sm, WHITE)
    draw_text_center("열쇠는 코드로 직접 그립니다.", 580, font_sm, WHITE)
    pygame.display.flip()

def main():
    scene = "menu"
    game = None

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if scene == "menu":
                    if e.key == pygame.K_1:
                        game = load_level(0, "stage")
                        scene = "game"
                    elif e.key == pygame.K_2:
                        game = load_level(0, "tutorial")
                        scene = "game"
                    elif e.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif scene == "game":
                    if e.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                    if e.key == pygame.K_ESCAPE:
                        scene = "menu"
                        game = None
                        continue

                    if e.key == pygame.K_r:
                        game = load_level(game["level_index"], game["mode"])
                        continue

                    if game["state"] == "playing":
                        if e.key == pygame.K_UP:
                            slide_snake(game, (0, -1))
                        elif e.key == pygame.K_DOWN:
                            slide_snake(game, (0, 1))
                        elif e.key == pygame.K_LEFT:
                            slide_snake(game, (-1, 0))
                        elif e.key == pygame.K_RIGHT:
                            slide_snake(game, (1, 0))

                    elif game["state"] == "clear":
                        if e.key == pygame.K_RETURN:
                            next_idx = game["level_index"] + 1
                            if next_idx >= game["level_total"]:
                                game["state"] = "finish"
                            else:
                                game = load_level(next_idx, game["mode"])

                    elif game["state"] == "finish":
                        if e.key == pygame.K_RETURN:
                            scene = "menu"
                            game = None
                        elif e.key == pygame.K_r:
                            game = load_level(0, game["mode"])

        if scene == "menu":
            draw_menu()
        else:
            draw_board(game)
            draw_overlay(game)
            pygame.display.flip()

if __name__ == "__main__":
    main()
