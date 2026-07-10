import pgzrun
import pygame
import os
from pgzero.actor import Actor
from tela_cheia import configurar_tela_cheia
import menu
import background
import audio
import math
from PIL import Image
intro = Actor("poluito_menu.png")
cena_do_carro = Actor("car.png")
game_background = Actor("background1.png")
player = Actor("player.png")

pygame.init()
pygame.mixer.init()

its_raining = False
chuva_sound = pygame.mixer.Sound(os.path.join("music", "rain.mp3"))
chuva_channel = None
#pygame.mixer.music.fadeout(1500) --> Sai da música com fadeout

new_size = (max(1, player.width // 2), max(1, player.height // 2))
player._orig_surf = pygame.transform.scale(player._orig_surf, new_size)
player._surf = player._orig_surf.copy()
player._update_pos()

WIDTH, HEIGHT = configurar_tela_cheia()
TITLE = "No Poluito"
FPS = 60
mode = "menu"
menu_button_rects = []
options_button_rects = []
menu_music_file = None
menu_music_playing = False
loading_timer = 0.0
loading_duration = 4.0
cutscene_timer = 0.0 
cutscene_duration = 10.0 # CARRO
fade_speed = 255.0 / 0.8
player_initialized = False
cutscene_lines = [
    "Após as abruptas mudanças climáticas, a cidade se tornou um lugar perigoso.",
    "A poluição tomou conta de tudo, e a vida se tornou um desafio constante.",
    "Mas há esperança. Há boatos de uma empresa que",
    "tem a tecnologia para reverter os danos causados ao meio ambiente."
]# História

quest = []
entry_block = None
entry_block_rect = None
joystick = None
joystick_connected = False
controller_deadzone = 0.25
controller_a_pressed_prev = False
menu_selection = 0
menu_input_cooldown = 0.0
menu_confirm_cooldown = 0.0
input_mode = "mouse"
options_selection = 0
options_input_cooldown = 0.0
options_confirm_cooldown = 0.0
tutorial_visible = False
tutorial_timer = 0.0
tutorial_duration = 5.0
tutorial_surface_cache = {}
e_prompt_visible = False
e_prompt_surface_cache = {}
e_prompt_frame_index = 0
e_prompt_frame_timer = 0.0
e_prompt_frame_duration = 0.12
tutorial_frame_index = 0
tutorial_frame_timer = 0.0
tutorial_frame_duration = 0.12


# try to find menu music at startup; user can drop a file named menu.ogg/menu.mp3 in project root or sounds/ or music/
menu_music_file = audio.find_menu_music()
# prefer explicit fnaf intro if available
fnaf_candidate = os.path.join(os.getcwd(), "music", "fnaf_intro.mp3")
'''        pygame.mixer.music.load(menu_music_file)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        #para parar áudio
        pygame.mixer.music.fadeout(800)
        pygame.mixer.music.stop()
        '''
if os.path.exists(fnaf_candidate):
    menu_music_file = fnaf_candidate


def ensure_controller():
    global joystick, joystick_connected
    if not pygame.get_init():
        pygame.init()

    if not pygame.joystick.get_init():
        pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        if joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        elif not joystick.get_init():
            joystick.init()
        joystick_connected = True
    else:
        joystick_connected = False
        if joystick is not None and joystick.get_init():
            joystick.quit()
        joystick = None

    return joystick_connected

ensure_controller()
def get_controller_move():
    ensure_controller()
    if not joystick_connected or joystick is None:
        return 0.0, 0.0

    axis_count = joystick.get_numaxes()
    left_x = joystick.get_axis(0) if axis_count > 0 else 0.0
    left_y = joystick.get_axis(1) if axis_count > 1 else 0.0

    if abs(left_x) < controller_deadzone:
        left_x = 0.0
    if abs(left_y) < controller_deadzone:
        left_y = 0.0

    return left_x, left_y


def get_controller_hat():
    ensure_controller()
    if not joystick_connected or joystick is None:
        return 0, 0
    if joystick.get_numhats() > 0:
        return joystick.get_hat(0)
    return 0, 0


def get_controller_button(button_index):
    ensure_controller()
    if not joystick_connected or joystick is None:
        return False
    if joystick.get_numbuttons() <= button_index:
        return False
    return bool(joystick.get_button(button_index))


def reset_player_position():
    global player_initialized, entry_block, entry_block_rect
    width, height = screen.surface.get_size()
    player.center = (width // 2, height -110)
    player_initialized = True
    player._surf = player._orig_surf.copy()
    if entry_block is None:
        entry_block = pygame.Rect(0, 0, 80, 20)
    entry_block.x = max(10, int(width * 0.5) - entry_block.width // 2)
    entry_block.y = max(10, int(height * 0.56))
    entry_block_rect = entry_block.copy()
    start_tutorial()


def set_input_mode(mode_name):
    global input_mode
    input_mode = mode_name


def get_tutorial_surface():
    global tutorial_surface_cache, tutorial_frame_index, tutorial_frame_timer
    asset_name = "tutorial_mov_xbox.gif" if input_mode == "controller" and joystick_connected else "tutorial_mov_pc.gif"
    if asset_name not in tutorial_surface_cache:
        path = os.path.join("images", asset_name)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                frames = []
                try:
                    while True:
                        frame = img.convert("RGBA")
                        frames.append(pygame.image.frombuffer(frame.tobytes(), frame.size, "RGBA"))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                tutorial_surface_cache[asset_name] = frames if frames else None
            except Exception:
                tutorial_surface_cache[asset_name] = None
        else:
            tutorial_surface_cache[asset_name] = None

    frames = tutorial_surface_cache.get(asset_name)
    if not frames:
        return None

    if len(frames) > 1:
        tutorial_frame_timer += 1 / FPS
        if tutorial_frame_timer >= tutorial_frame_duration:
            tutorial_frame_timer = 0.0
            tutorial_frame_index = (tutorial_frame_index + 1) % len(frames)
        return frames[tutorial_frame_index]
    return frames[0]


def start_tutorial():
    global tutorial_visible, tutorial_timer, tutorial_frame_index, tutorial_frame_timer
    tutorial_visible = True
    tutorial_timer = 0.0
    tutorial_frame_index = 0
    tutorial_frame_timer = 0.0


def get_e_prompt_surface():
    global e_prompt_surface_cache, e_prompt_frame_index, e_prompt_frame_timer
    asset_name = "E.gif"
    if asset_name not in e_prompt_surface_cache:
        path = os.path.join("images", asset_name)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                frames = []
                try:
                    while True:
                        frame = img.convert("RGBA")
                        frames.append(pygame.image.frombuffer(frame.tobytes(), frame.size, "RGBA"))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                e_prompt_surface_cache[asset_name] = frames if frames else None
            except Exception:
                e_prompt_surface_cache[asset_name] = None
        else:
            e_prompt_surface_cache[asset_name] = None

    frames = e_prompt_surface_cache.get(asset_name)
    if not frames:
        return None

    if len(frames) > 1:
        e_prompt_frame_timer += 1 / FPS
        if e_prompt_frame_timer >= e_prompt_frame_duration:
            e_prompt_frame_timer = 0.0
            e_prompt_frame_index = (e_prompt_frame_index + 1) % len(frames)
        return frames[e_prompt_frame_index]
    return frames[0]


def get_input_mode_label():
    return "Controle Xbox" if input_mode == "controller" else "Mouse/Teclado"


def activate_menu_selection():
    global mode, loading_timer, cutscene_timer, player_initialized
    action = menu.get_menu_action_from_index(menu_selection)
    if action == "game":
        mode = "loading"
        loading_timer = 0.0
        cutscene_timer = 0.0
        player_initialized = False
        start_tutorial()
    elif action:
        mode = action


def draw_game():
    global its_raining, chuva_channel
    width, height = screen.surface.get_size()

    background.draw_background(screen, game_background)
    menu.draw_rain_effect(screen)
    if not player_initialized:
        reset_player_position()
    player.draw()

    if entry_block_rect is not None:
        pass # para saber o lugar exato do bloco de entrada, descomente a linha abaixo
        #pygame.draw.rect(screen.surface, (0, 0, 0, 0), entry_block_rect) 

    if its_raining:
        chuva_sound.set_volume(0.5)
        if chuva_channel is None or not chuva_channel.get_busy():
            chuva_channel = chuva_sound.play(-1)
    else:
        if chuva_channel is not None:
            chuva_channel.stop()
            chuva_channel = None

    global tutorial_visible
    if e_prompt_visible:
        prompt_surface = get_e_prompt_surface()
        if prompt_surface is not None:
            scaled_prompt = pygame.transform.scale(prompt_surface, (70, 70))
            prompt_x = int(player.x - scaled_prompt.get_width() / 2)
            prompt_y = max(10, int(player.y - scaled_prompt.get_height() - 90))
            screen.surface.blit(scaled_prompt, (prompt_x, prompt_y))

    if tutorial_visible:
        tutorial_surface = get_tutorial_surface()
        if tutorial_surface is not None:
            scale_factor = 0.35
            new_width = max(1, int(tutorial_surface.get_width() * scale_factor))
            new_height = max(1, int(tutorial_surface.get_height() * scale_factor))
            scaled_surface = pygame.transform.scale(tutorial_surface, (new_width, new_height))
            tutorial_x = int(player.x - scaled_surface.get_width() / 2)
            tutorial_y = max(10, int(player.y - scaled_surface.get_height() - 40))
            tutorial_x = max(10, min(width - scaled_surface.get_width() - 10, tutorial_x))
            screen.surface.blit(scaled_surface, (tutorial_x, tutorial_y))

def draw_loading():
    width, height = screen.surface.get_size()
    screen.surface.fill((0, 0, 0))

    loading_font = pygame.font.SysFont("arial", 36, bold=True)
    warning_font = pygame.font.SysFont("arial", 22)

    progress = min(loading_timer / 0.8, 1.0)
    if loading_timer > loading_duration - 0.8:
        progress = max(0.0, 1.0 - ((loading_timer - (loading_duration - 0.8)) / 0.8))

    alpha = int(progress * 255)

    loading_text = loading_font.render("Loading...", True, (255, 255, 255))
    warning_text = warning_font.render(
        "Aviso: este jogo possui luzes piscando e pode causar desconforto.",
        True,
        (255, 220, 220),
    )

    loading_surface = loading_text.copy()
    warning_surface = warning_text.copy()
    loading_surface.set_alpha(alpha)
    warning_surface.set_alpha(alpha)

    loading_x = (width - loading_text.get_width()) // 2
    loading_y = (height - loading_text.get_height()) // 2
    warning_x = (width - warning_text.get_width()) // 2
    warning_y = loading_y + loading_text.get_height() + 24

    screen.surface.blit(loading_surface, (loading_x, loading_y))
    screen.surface.blit(warning_surface, (warning_x, warning_y))


def draw_menu():
    menu.draw_menu(screen, intro, menu_button_rects, menu_selection, joystick_connected and input_mode == "controller")


def draw_options():
    width, height = screen.surface.get_size()
    menu.draw_background(screen, intro)
    screen.surface.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    title_font = pygame.font.SysFont("arial", 42, bold=True)
    body_font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    title = title_font.render("Opções", True, (255, 255, 255))
    screen.surface.blit(title, (int(width * 0.08), int(height * 0.16)))

    options = ["Mouse/Teclado", "Controle Xbox", "Voltar"]
    base_x = int(width * 0.12)
    start_y = int(height * 0.32)
    gap = 64
    mx, my = pygame.mouse.get_pos()
    options_button_rects.clear()

    status_text = small_font.render(f"Entrada atual: {get_input_mode_label()}", True, (220, 220, 220))
    screen.surface.blit(status_text, (base_x, int(height * 0.24)))

    if input_mode == "controller" and not joystick_connected:
        warning_text = small_font.render("Controle não detectado. Ele entrará em uso quando estiver conectado.", True, (255, 180, 180))
        screen.surface.blit(warning_text, (base_x, int(height * 0.28)))

    for i, label in enumerate(options):
        y = start_y + i * gap
        text = body_font.render(label, True, (220, 220, 220))
        text_rect = pygame.Rect(base_x, y, text.get_width(), text.get_height())
        hovered = text_rect.collidepoint((mx, my))
        active = hovered or i == options_selection
        color = (200, 150, 255) if active else (220, 220, 220)
        text = body_font.render(label, True, color)
        screen.surface.blit(text, (base_x, y))
        options_button_rects.append(pygame.Rect(text_rect.x, text_rect.y - 8, text_rect.width, text_rect.height + 16))


def draw_cutscene():
    width, height = screen.surface.get_size()
    background.draw_background(screen, cena_do_carro)

    title_font = pygame.font.SysFont("arial", 36, bold=True)
    body_font = pygame.font.SysFont("arial", 15, bold=True)

    title_text = title_font.render("História", True, (255, 50, 255))
    title_rect = title_text.get_rect(center=(width // 2, 80))
    title_bg = pygame.Surface((title_rect.width + 20, title_rect.height + 14), pygame.SRCALPHA)
    title_bg.fill((0, 0, 0, 170))
    screen.surface.blit(title_bg, (title_rect.x - 10, title_rect.y - 7))
    screen.surface.blit(title_text, title_rect)

    start_y = 170
    for idx, line in enumerate(cutscene_lines):
        text_surface = body_font.render(line, True, (255, 50, 255))
        text_rect = text_surface.get_rect(center=(width // 2, start_y + idx * 52))
        line_bg = pygame.Surface((text_rect.width + 18, text_rect.height + 10), pygame.SRCALPHA)
        line_bg.fill((0, 0, 0, 160))
        screen.surface.blit(line_bg, (text_rect.x - 9, text_rect.y - 5))
        screen.surface.blit(text_surface, text_rect)


def draw():
    screen.clear()
    if mode == "menu":
        draw_menu()
    elif mode == "game":
        draw_game()
    elif mode == "options":
        draw_options()
    elif mode == "loading":
        draw_loading()
    elif mode == "car_cutscene":
        draw_cutscene()


def update(dt):
    pygame.mouse.set_visible(True)
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    global menu_music_playing, menu_music_file, mode, loading_timer, cutscene_timer, player_initialized
    global menu_selection, menu_input_cooldown, menu_confirm_cooldown, controller_a_pressed_prev
    global options_selection, options_input_cooldown, options_confirm_cooldown, tutorial_visible, tutorial_timer
    global e_prompt_visible, its_raining
    '''
if mode == "game":
    pygame.mixer.music.load(chuva_sound)
    pygame.mixer.music.play(-1)
else:
    pygame.mixer.music.fadeout(1500)
'''

    its_raining = mode == "game"
    
    
    
    if mode == "loading":
        loading_timer += dt
        if loading_timer >= loading_duration:
            mode = "car_cutscene"
            loading_timer = 0.0
            cutscene_timer = 0.0
    elif mode == "car_cutscene":
        cutscene_timer += dt
        if cutscene_timer >= cutscene_duration:
            mode = "game"
            cutscene_timer = 0.0
            player_initialized = False
            start_tutorial()
    elif mode == "game":#cenário 1
        if not player_initialized:
            reset_player_position()

        width, height = screen.surface.get_size()
        speed = 100 * dt
        keys = pygame.key.get_pressed()

        if input_mode == "controller" and joystick_connected:
            move_x, move_y = get_controller_move()
        else:
            move_x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
            move_y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        move_x = max(-1.0, min(1.0, move_x))
        move_y = max(-1.0, min(1.0, move_y))

        if move_x < 0:
            player._surf = pygame.transform.flip(player._orig_surf.copy(), True, False)
        elif move_x > 0:
            player._surf = player._orig_surf.copy()

        moved = False
        if move_x != 0:
            next_x = player.x + move_x * speed
            if move_x > 0 and next_x < width - player.width / 2:
                player.x = next_x
                moved = True
            elif move_x < 0 and next_x > player.width / 2:
                player.x = next_x
                moved = True

        if move_y != 0:
            next_y = player.y + move_y * speed
            if move_y > 0 and next_y < height - player.height / 2:
                player.y = next_y
                moved = True
            elif move_y < 0 and next_y > height / 2 + 55:
                player.y = next_y
                moved = True

        if entry_block_rect is not None:
            player_rect = pygame.Rect(int(player.x - player.width / 2), int(player.y - player.height / 2), player.width, player.height)
            if player_rect.colliderect(entry_block_rect):
                e_prompt_visible = True
            else:
                e_prompt_visible = False

        if moved and tutorial_visible:
            tutorial_visible = False

        if tutorial_visible:
            tutorial_timer += dt
            if tutorial_timer >= tutorial_duration:
                tutorial_visible = False

    if mode == "menu":
        ensure_controller()
        menu_input_cooldown = max(0.0, menu_input_cooldown - dt)
        menu_confirm_cooldown = max(0.0, menu_confirm_cooldown - dt)

        if input_mode == "controller" and joystick_connected:
            controller_x, controller_y = get_controller_move()
            hat_x, hat_y = get_controller_hat()
            direction = 0
            if controller_y < -controller_deadzone or hat_y < 0:
                direction = -1
            elif controller_y > controller_deadzone or hat_y > 0:
                direction = 1

            if direction != 0 and menu_input_cooldown <= 0.0:
                menu_selection = max(0, min(len(menu.MENU_ITEMS) - 1, menu_selection + direction))
                menu_input_cooldown = 0.2

            a_pressed = get_controller_button(0)
            if a_pressed and not controller_a_pressed_prev and menu_confirm_cooldown <= 0.0:
                menu_confirm_cooldown = 0.25
                activate_menu_selection()
            controller_a_pressed_prev = a_pressed

    if mode == "options":
        ensure_controller()
        options_input_cooldown = max(0.0, options_input_cooldown - dt)
        options_confirm_cooldown = max(0.0, options_confirm_cooldown - dt)

        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction = 1

        if input_mode == "controller" and joystick_connected:
            controller_x, controller_y = get_controller_move()
            hat_x, hat_y = get_controller_hat()
            if controller_y < -controller_deadzone or hat_y < 0:
                direction = -1
            elif controller_y > controller_deadzone or hat_y > 0:
                direction = 1

        if direction != 0 and options_input_cooldown <= 0.0:
            options_selection = max(0, min(2, options_selection + direction))
            options_input_cooldown = 0.2

        confirm_key = keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
        a_pressed = get_controller_button(0)
        if (confirm_key or a_pressed) and not controller_a_pressed_prev and options_confirm_cooldown <= 0.0:
            options_confirm_cooldown = 0.25
            if options_selection == 0:
                set_input_mode("mouse")
            elif options_selection == 1:
                set_input_mode("controller")
            else:
                mode = "menu"
                options_selection = 0
            controller_a_pressed_prev = True
        elif not confirm_key and not a_pressed:
            controller_a_pressed_prev = False

    if mode == "car_cutscene":
        if get_controller_button(0) and not controller_a_pressed_prev:
            mode = "game"
            cutscene_timer = 0.0
            player_initialized = False
        controller_a_pressed_prev = get_controller_button(0)

    # handle menu music playback
    try:
        if mode == "menu":
            if menu_music_file and not menu_music_playing:
                menu_music_playing = audio.play_menu_music(menu_music_file)
        else:
            if menu_music_playing:
                audio.stop_menu_music()
                menu_music_playing = False
    except Exception:
        pass
def on_mouse_down(pos, button):
    global mode, loading_timer, cutscene_timer

    if button != 1:
        return

    width, height = screen.surface.get_size()
    if mode == "menu":
        action = menu.get_menu_action(pos, menu_button_rects)
        if action == "game":
            mode = "loading"
            loading_timer = 0.0
            cutscene_timer = 0.0
            player_initialized = False
        elif action:
            mode = action
    elif mode == "options":
        for idx, rect in enumerate(options_button_rects):
            if rect.collidepoint(pos):
                if idx == 0:
                    set_input_mode("mouse")
                elif idx == 1:
                    set_input_mode("controller")
                else:
                    mode = "menu"
                    options_selection = 0
                break
    elif mode == "car_cutscene":
        mode = "game"
        cutscene_timer = 0.0
        player_initialized = False
    

pgzrun.go()