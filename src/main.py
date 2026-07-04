import sys
import pygame
from config import DEFAULT_RESOLUTION, LOGICAL_SIZE
from TicSystem import TicSystem

TICS_PER_SECOND = 2


def get_viewport_rect(screen_size, resolution, is_fullscreen):
    if not is_fullscreen:
        return pygame.Rect((0, 0), resolution)

    viewport = pygame.Rect((0, 0), resolution)
    viewport.center = (screen_size[0] // 2, screen_size[1] // 2)
    return viewport


def main():
    debug_enabled = "debug" in sys.argv[1:]

    pygame.init()
    window = pygame.Window(size=DEFAULT_RESOLUTION, resizable=True)
    screen = window.get_surface()
    game_surface = pygame.Surface(LOGICAL_SIZE).convert()
    current_resolution = DEFAULT_RESOLUTION
    fullscreen = False
    windowed_fullscreen = False
    viewport_rect = pygame.Rect((0, 0), current_resolution)
    clock = pygame.time.Clock()
    tic_system = TicSystem(TICS_PER_SECOND)
    running = True
    dt = 0

    # ImageManager loads convert_alpha() assets at import time, after display setup.
    import GameState

    game_state = GameState.GameState(game_surface, DEFAULT_RESOLUTION, debug_enabled, tic_system)

    def to_logical_event(event):
        nonlocal viewport_rect

        if not hasattr(event, "pos"):
            return event

        viewport_rect = get_viewport_rect(
            screen.get_size(),
            current_resolution,
            fullscreen or windowed_fullscreen,
        )
        logical_width, logical_height = LOGICAL_SIZE
        x, y = event.pos

        if not viewport_rect.collidepoint(event.pos):
            logical_pos = (-1, -1)
        else:
            viewport_x = x - viewport_rect.left
            viewport_y = y - viewport_rect.top
            logical_pos = (
                int(viewport_x * logical_width / viewport_rect.width),
                int(viewport_y * logical_height / viewport_rect.height),
            )

        event_data = event.dict.copy()
        event_data["pos"] = logical_pos
        return pygame.event.Event(event.type, event_data)

    def set_window_maximized(maximized):
        if maximized:
            window.maximize()
        else:
            window.restore()

        focus_window()

    def focus_window():
        try:
            window.show()
            window.focus()
        except pygame.error:
            return

    def apply_display_change(resolution, is_fullscreen, is_windowed_fullscreen):
        if is_fullscreen:
            window.set_fullscreen(desktop=True)
            focus_window()
            display = window.get_surface()
            viewport = get_viewport_rect(display.get_size(), resolution, True)
            return display, viewport

        window.set_windowed()
        window.size = resolution
        set_window_maximized(is_windowed_fullscreen)
        focus_window()
        display = window.get_surface()
        viewport = get_viewport_rect(display.get_size(), resolution, is_windowed_fullscreen)
        return display, viewport

    def draw_game_surface():
        screen.fill("black")

        if viewport_rect.size == LOGICAL_SIZE:
            screen.blit(game_surface, viewport_rect.topleft)
            return

        scaled_surface = pygame.transform.smoothscale(game_surface, viewport_rect.size)
        screen.blit(scaled_surface, viewport_rect.topleft)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.WINDOWMAXIMIZED:
                fullscreen = False
                windowed_fullscreen = True
                game_state.set_display_modes(False, True, False)
                viewport_rect = get_viewport_rect(screen.get_size(), current_resolution, True)
            elif event.type == pygame.WINDOWRESTORED:
                fullscreen = False
                windowed_fullscreen = False
                game_state.set_display_modes(False, False, False)
                viewport_rect = get_viewport_rect(screen.get_size(), current_resolution, False)
            elif event.type in (pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED):
                viewport_rect = get_viewport_rect(
                    screen.get_size(),
                    current_resolution,
                    fullscreen or windowed_fullscreen,
                )
            else:
                game_state.handle_event(to_logical_event(event))

        tics_elapsed = tic_system.update(dt)
        game_state.update(dt, tics_elapsed, tic_system.tics_per_second)
        game_state.set_debug_framerate(clock.get_fps())

        display_change = game_state.consume_display_change()
        if display_change is not None:
            current_resolution, fullscreen, windowed_fullscreen = display_change
            screen, viewport_rect = apply_display_change(current_resolution, fullscreen, windowed_fullscreen)

        game_surface.fill("purple")

        game_state.draw()
        draw_game_surface()

        window.flip()

        dt = clock.tick(60) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
