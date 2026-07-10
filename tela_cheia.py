import pygame
from pgzero import game as pgzero_game


def configurar_tela_cheia():
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h
    pgzero_game.DISPLAY_FLAGS = pygame.FULLSCREEN
    return width, height
