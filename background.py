import pygame


def draw_background(screen, intro):
    width, height = screen.surface.get_size()
    scale = min(width / intro.width, height / intro.height)
    scaled_width = max(1, int(intro.width * scale))
    scaled_height = max(1, int(intro.height * scale))
    scaled_image = pygame.transform.smoothscale(intro._surf, (scaled_width, scaled_height))
    x = (width - scaled_width) // 2
    y = (height - scaled_height) // 2
    screen.surface.blit(scaled_image, (x, y))
