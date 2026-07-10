import pygame
import math
import random

MENU_ITEMS = ["Play No Poluito", "Continue", "Options"]
RAIN_DROPS = []


def draw_rain_effect(screen):
    global RAIN_DROPS
    width, height = screen.surface.get_size()

    if not RAIN_DROPS or len(RAIN_DROPS) < max(80, width // 8):
        RAIN_DROPS = []
        for _ in range(max(80, width // 8)):
            RAIN_DROPS.append({
                "x": random.randint(0, width + 20),
                "y": random.randint(-height, height),
                "length": random.randint(8, 18),
                "speed": random.uniform(8, 16),
                "drift": random.uniform(0.2, 0.6),
                "alpha": random.randint(70, 180),
            })

    rain_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for drop in RAIN_DROPS:
        drop["y"] += drop["speed"]
        drop["x"] -= drop["drift"]

        if drop["y"] > height + 20 or drop["x"] < -10:
            drop["x"] = random.randint(0, width + 20)
            drop["y"] = random.randint(-80, -10)
            drop["length"] = random.randint(8, 18)
            drop["speed"] = random.uniform(8, 16)
            drop["drift"] = random.uniform(0.2, 0.6)
            drop["alpha"] = random.randint(70, 180)

        pygame.draw.line(
            rain_surface,
            (180, 210, 255, drop["alpha"]),
            (drop["x"], drop["y"]),
            (drop["x"] - 2, drop["y"] + drop["length"]),
            1,
        )

    screen.surface.blit(rain_surface, (0, 0))


def draw_menu(screen, intro, menu_button_rects, selected_index=None, controller_connected=False):
    width, height = screen.surface.get_size()
    draw_background(screen, intro)


    title_font = pygame.font.SysFont("arial", 48, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 24)
    title = title_font.render("NO, POLUÍTO!", True, (255, 255, 255))
    subtitle = subtitle_font.render("Escolha uma opção para começar", True, (220, 220, 220))
    title_x = int(width * 0.06)
    subtitle_x = int(width * 0.06)
    screen.surface.blit(title, (title_x, height // 2 - 140))
    screen.surface.blit(subtitle, (subtitle_x, height // 2 - 90))

    font = pygame.font.SysFont("arial", 36)
    small_font = pygame.font.SysFont("arial", 30)

    base_x = int(width * 0.12)
    start_y = height // 2 - 60
    gap = 64

    menu_button_rects.clear()

    t = pygame.time.get_ticks() / 1000.0
    pulse = (math.sin(t * 3.0) + 1.0) / 2.0
    mx, my = pygame.mouse.get_pos()

    for i, label in enumerate(MENU_ITEMS):
        y = start_y + i * gap
        f = font if i == 0 else small_font
        text = f.render(label, True, (210, 210, 210))
        screen.surface.blit(f.render(label, True, (0, 0, 0, 180)), (base_x + 4, y + 4))

        text_rect = pygame.Rect(base_x, y, text.get_width(), text.get_height())
        hovered = text_rect.collidepoint((mx, my))
        active = (i == selected_index) if controller_connected and selected_index is not None else hovered
        color = (200, 150, 255) if active else (220, 220, 220)
        text = f.render(label, True, color)
        screen.surface.blit(text, (base_x, y))

        if active:
            underline_w = int(text.get_width() * 1.05)
            underline_h = 3
            underline_x = base_x
            underline_y = y + text.get_height() + 8
            underline_alpha = int(200 * (0.5 + 0.5 * pulse))

            grad_h = 30
            g_surf = pygame.Surface((underline_w, grad_h + underline_h), pygame.SRCALPHA)
            for gy in range(grad_h):
                a = int((gy / float(grad_h)) * underline_alpha)
                pygame.draw.rect(g_surf, (150, 80, 220, a), (0, gy, underline_w, 1))
            pygame.draw.rect(g_surf, (150, 80, 220, underline_alpha), (0, grad_h, underline_w, underline_h))
            screen.surface.blit(g_surf, (underline_x, underline_y - grad_h))

        menu_button_rects.append(pygame.Rect(text_rect.x, text_rect.y - 8, text_rect.width, text_rect.height + 16))


def get_menu_action(pos, menu_button_rects):
    for idx, rect in enumerate(menu_button_rects):
        if rect.collidepoint(pos):
            return get_menu_action_from_index(idx)
    return None


def get_menu_action_from_index(index):
    if index == 0:
        return "game"
    if index == 1:
        return "continue"
    return "options"


# Avoid circular imports by importing local background helper here.
def draw_background(screen, intro):
    # imported locally to prevent module import cycle if background imports menu
    import background
    background.draw_background(screen, intro)
    
