import pygame
import random
import sys

# ── Constants ──────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 600, 600
GRID_SIZE          = 20
COLS               = WINDOW_W // GRID_SIZE
ROWS               = WINDOW_H // GRID_SIZE
FPS                = 10

# Colours
BG_COLOR      = (15,  17,  26)
GRID_COLOR    = (25,  28,  40)
SNAKE_HEAD    = (80,  220, 120)
SNAKE_BODY    = (50,  170,  90)
FOOD_COLOR    = (255,  80,  80)
SCORE_COLOR   = (220, 220, 240)
OVERLAY_BG    = (15,  17,  26, 210)
ACCENT        = (80,  220, 120)

# Directions
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# ── Helper ─────────────────────────────────────────────────────────────────────

def random_food(snake_cells):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake_cells:
            return pos

def draw_grid(surface):
    for x in range(0, WINDOW_W, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_H))
    for y in range(0, WINDOW_H, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_W, y))

def draw_snake(surface, snake):
    for i, (gx, gy) in enumerate(snake):
        rect = pygame.Rect(gx * GRID_SIZE + 1, gy * GRID_SIZE + 1,
                           GRID_SIZE - 2, GRID_SIZE - 2)
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        radius = 6 if i == 0 else 4
        pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_food(surface, food, tick):
    gx, gy = food
    pulse = abs((tick % 20) - 10) / 10          # 0 → 1 → 0 every 20 frames
    size  = int((GRID_SIZE - 4) + pulse * 3)
    offset = (GRID_SIZE - size) // 2
    rect = pygame.Rect(gx * GRID_SIZE + offset, gy * GRID_SIZE + offset, size, size)
    pygame.draw.ellipse(surface, FOOD_COLOR, rect)

def draw_score(surface, font, score, high_score):
    s_text = font.render(f"Score: {score}", True, SCORE_COLOR)
    h_text = font.render(f"Best:  {high_score}", True, SCORE_COLOR)
    surface.blit(s_text, (8, 6))
    surface.blit(h_text, (WINDOW_W - h_text.get_width() - 8, 6))

def draw_overlay(surface, big_font, med_font, title, subtitle):
    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill(OVERLAY_BG)
    surface.blit(overlay, (0, 0))

    t = big_font.render(title, True, ACCENT)
    surface.blit(t, (WINDOW_W // 2 - t.get_width() // 2, WINDOW_H // 2 - 60))

    for i, line in enumerate(subtitle):
        s = med_font.render(line, True, SCORE_COLOR)
        surface.blit(s, (WINDOW_W // 2 - s.get_width() // 2,
                         WINDOW_H // 2 + 10 + i * 32))

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Snake")
    clock   = pygame.time.Clock()

    big_font = pygame.font.SysFont("consolas", 48, bold=True)
    med_font = pygame.font.SysFont("consolas", 22)
    sml_font = pygame.font.SysFont("consolas", 18)

    # ── Game state ──
    def new_game():
        snake     = [(COLS // 2, ROWS // 2)]
        direction = RIGHT
        food      = random_food(set(snake))
        return snake, direction, food, 0

    snake, direction, food, score = new_game()
    high_score   = 0
    state        = "start"   # "start" | "playing" | "dead"
    tick         = 0
    pending_dir  = direction

    while True:
        clock.tick(FPS)
        tick += 1

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if state in ("start", "dead"):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        snake, direction, food, score = new_game()
                        pending_dir = direction
                        state = "playing"
                elif state == "playing":
                    if event.key == pygame.K_UP    and direction != DOWN:
                        pending_dir = UP
                    elif event.key == pygame.K_DOWN  and direction != UP:
                        pending_dir = DOWN
                    elif event.key == pygame.K_LEFT  and direction != RIGHT:
                        pending_dir = LEFT
                    elif event.key == pygame.K_RIGHT and direction != LEFT:
                        pending_dir = RIGHT
                    # WASD support
                    elif event.key == pygame.K_w and direction != DOWN:
                        pending_dir = UP
                    elif event.key == pygame.K_s and direction != UP:
                        pending_dir = DOWN
                    elif event.key == pygame.K_a and direction != RIGHT:
                        pending_dir = LEFT
                    elif event.key == pygame.K_d and direction != LEFT:
                        pending_dir = RIGHT
                    elif event.key == pygame.K_ESCAPE:
                        state = "start"

        # ── Update ────────────────────────────────────────────────────────────
        if state == "playing":
            direction = pending_dir
            hx, hy = snake[0]
            dx, dy = direction
            new_head = ((hx + dx) % COLS, (hy + dy) % ROWS)

            # Wall collision (no wrap-around — game over)
            nx, ny = hx + dx, hy + dy
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                state = "dead"
                high_score = max(high_score, score)
            elif new_head in snake[1:]:
                state = "dead"
                high_score = max(high_score, score)
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = random_food(set(snake))
                else:
                    snake.pop()

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_food(screen, food, tick)
        draw_snake(screen, snake)
        draw_score(screen, sml_font, score, high_score)

        if state == "start":
            draw_overlay(screen, big_font, med_font,
                         "SNAKE",
                         ["Arrow keys / WASD to move",
                          "Press ENTER or SPACE to start"])
        elif state == "dead":
            draw_overlay(screen, big_font, med_font,
                         "GAME OVER",
                         [f"Score: {score}",
                          "Press ENTER or SPACE to restart"])

        pygame.display.flip()

if __name__ == "__main__":
    main()