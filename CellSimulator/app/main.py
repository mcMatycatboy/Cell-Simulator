import pygame
import sys

SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
GRID_SIZE = 100
CELL_SIZE = 20
ZOOM_STEP = 1.1

COLORS = {
    0: (255, 0, 0),
    1: (0, 255, 0),
    2: (0, 0, 255),
    3: (30, 30, 30),
}

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

grid = [[3 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
zoom = 1.0
offset_x, offset_y = 0, 0
painting = False
current_state = 0
simulation_running = False

simulation_speed = 500
last_update_time = 0

tick_counter = 0

STATE_BUTTON_SIZE = 50
state_buttons = [(SCREEN_WIDTH//2 - 80 + i * (STATE_BUTTON_SIZE + 10), SCREEN_HEIGHT - 120) for i in range(3)]

slider_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 30, 400, 10)
slider_handle = pygame.Rect(slider_rect.x + 200, slider_rect.y - 5, 10, 20)
dragging_slider = False

do_step_button = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 160, 40)
clear_button = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 130, 160, 40)

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell_state = grid[y][x]
            color = COLORS[cell_state]
            size = int(CELL_SIZE * zoom)
            draw_x = x * size + offset_x
            draw_y = y * size + offset_y
            if -size < draw_x < SCREEN_WIDTH and -size < draw_y < SCREEN_HEIGHT:
                pygame.draw.rect(screen, color, (draw_x, draw_y, size - 1, size - 1))

def draw_ui():
    for i, (bx, by) in enumerate(state_buttons):
        pygame.draw.rect(screen, COLORS[i], (bx, by, STATE_BUTTON_SIZE, STATE_BUTTON_SIZE))
        if i == current_state:
            pygame.draw.rect(screen, (255, 255, 255), (bx, by, STATE_BUTTON_SIZE, STATE_BUTTON_SIZE), 3)

    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
    pygame.draw.rect(screen, (255, 255, 0), slider_handle)

    speed_text = font.render(f"Speed: {simulation_speed} ms", True, (255, 255, 255))
    screen.blit(speed_text, (slider_rect.x, slider_rect.y - 35))

    tick_text = font.render(f"Tick: {tick_counter}", True, (255, 255, 255))
    screen.blit(tick_text, (slider_rect.x + 280, slider_rect.y - 35))

    pygame.draw.rect(screen, (50, 150, 255), do_step_button)
    step_text = font.render("Play 1 Tick", True, (0, 0, 0))
    screen.blit(step_text, (do_step_button.x + 25, do_step_button.y + 5))

    pygame.draw.rect(screen, (200, 50, 50), clear_button)
    clear_text = font.render("Clean Grid", True, (255, 255, 255))
    screen.blit(clear_text, (clear_button.x + 5, clear_button.y + 5))

def update_simulation():
    new_grid = [row.copy() for row in grid]
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            current = grid[y][x]
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        neighbors.append(grid[ny][nx])

            if current == 0 and 2 in neighbors:
                new_grid[y][x] = 1
            elif current == 0 and 1 in neighbors:
                new_grid[y][x] = 3
            elif current == 1 and 1 in neighbors:
                new_grid[y][x] = 2
            elif current == 2 and 2 in neighbors:
                new_grid[y][x] = 0
            elif current == 3 and 0 in neighbors and 2 in neighbors:
                new_grid[y][x] = 1
            elif current == 1 and 0 in neighbors:
                new_grid[y][x] = 3
    return new_grid

def clear_grid():
    global grid
    grid = [[3 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

while True:
    screen.fill((10, 10, 10))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                simulation_running = not simulation_running

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 1:
                painting = True
                for i, (bx, by) in enumerate(state_buttons):
                    if pygame.Rect(bx, by, STATE_BUTTON_SIZE, STATE_BUTTON_SIZE).collidepoint(mx, my):
                        current_state = i
                if slider_handle.collidepoint(mx, my):
                    dragging_slider = True
                elif do_step_button.collidepoint(mx, my):
                    grid = update_simulation()
                    tick_counter += 1
                elif clear_button.collidepoint(mx, my):
                    clear_grid()
                    tick_counter = 0
            elif event.button == 3:
                painting = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                painting = False
                dragging_slider = False

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if painting and not dragging_slider:
                size = int(CELL_SIZE * zoom)
                gx = (mx - offset_x) // size
                gy = (my - offset_y) // size
                if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                    if pygame.mouse.get_pressed()[2]:
                        grid[gy][gx] = 3
                    else:
                        grid[gy][gx] = current_state
            if dragging_slider:
                slider_handle.centerx = max(slider_rect.left, min(slider_rect.right, mx))
                rel_pos = (slider_handle.centerx - slider_rect.left) / slider_rect.width
                simulation_speed = int(100 + (1.0 - rel_pos) * 1000)

        elif event.type == pygame.MOUSEWHEEL:
            old_zoom = zoom
            if event.y > 0:
                zoom *= ZOOM_STEP
            elif event.y < 0:
                zoom /= ZOOM_STEP
            zoom = max(0.1, min(zoom, 10))
            mx, my = pygame.mouse.get_pos()
            offset_x = mx - (mx - offset_x) * (zoom / old_zoom)
            offset_y = my - (my - offset_y) * (zoom / old_zoom)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                offset_x += 20
            elif event.key == pygame.K_RIGHT:
                offset_x -= 20
            elif event.key == pygame.K_UP:
                offset_y += 20
            elif event.key == pygame.K_DOWN:
                offset_y -= 20

    if simulation_running and current_time - last_update_time > simulation_speed:
        grid = update_simulation()
        last_update_time = current_time
        tick_counter += 1

    draw_grid()
    draw_ui()
    pygame.display.flip()
    clock.tick(60)
