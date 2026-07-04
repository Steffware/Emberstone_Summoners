import pygame


DEFAULT_SIZE = (144, 24)
FILL_INSET = pygame.Rect(5, 4, 134, 16)


def draw_progress_bar(screen, image_manager, rect, percentage):
    empty_bar = pygame.transform.scale(image_manager.get_progressbar("progressbar_empty_png"), rect.size)
    fill_tile = image_manager.get_progressbar("progressbar_fill_png")
    fill_area = scaled_fill_area(rect)
    fill_width = int(fill_area.width * max(0, min(percentage, 100)) / 100)

    screen.blit(empty_bar, rect)

    if fill_width > 0:
        fill_rect = pygame.Rect(fill_area.left, fill_area.top, fill_width, fill_area.height)
        tile_fill(screen, fill_tile, fill_rect)


def scaled_fill_area(rect):
    scale_x = rect.width / DEFAULT_SIZE[0]
    scale_y = rect.height / DEFAULT_SIZE[1]
    return pygame.Rect(
        rect.left + round(FILL_INSET.left * scale_x),
        rect.top + round(FILL_INSET.top * scale_y),
        round(FILL_INSET.width * scale_x),
        round(FILL_INSET.height * scale_y),
    )


def tile_fill(screen, fill_tile, fill_rect):
    scaled_tile = pygame.transform.scale(fill_tile, (fill_tile.get_width(), fill_rect.height))

    for x in range(fill_rect.left, fill_rect.right, scaled_tile.get_width()):
        source = pygame.Rect(0, 0, min(scaled_tile.get_width(), fill_rect.right - x), fill_rect.height)
        screen.blit(scaled_tile, (x, fill_rect.top), source)
