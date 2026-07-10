import os
import pygame


def find_menu_music():
    candidates = [
        "menu.ogg",
        "menu.mp3",
        "menu.wav",
        os.path.join("sounds", "menu.ogg"),
        os.path.join("sounds", "menu.mp3"),
        os.path.join("music", "menu.ogg"),
        os.path.join("music", "menu.mp3"),
    ]
    for p in candidates:
        if os.path.isabs(p):
            check = p
        else:
            check = os.path.join(os.getcwd(), p)
        if os.path.exists(check):
            return check
    return None


def play_menu_music(menu_music_file):
    if not menu_music_file:
        return False
    try:
        pygame.mixer.music.load(menu_music_file)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        return True
    except Exception:
        return False


def stop_menu_music():
    try:
        pygame.mixer.music.fadeout(800)
    except Exception:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
