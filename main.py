import os
import sys
import json
import threading
import warnings
import signal
import platform
import numpy as np


print(f"[Info] Running on platform: {platform.system()} {platform.release()}")
print(f"[Info] Architecture: {platform.architecture()[0]}")
print(f"[Info] Python version: {platform.python_version()}")
print(f"[Info] Python implementation: {platform.python_implementation()}")
print(f"[Info] Python executable: {sys.executable}")

dll_arch = "64" if platform.architecture()[0] == "64bit" else "32"

print(f"[Info] Using DLL architecture: {dll_arch}-bit")


# Suppress Pygame warning + print
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame.locals import *
from PIL import Image
import pystray

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes
    import win32gui
    import win32con
    import win32api
else:
    print("[Error] This script is designed for Windows only.")
    sys.exit(1)

if os.path.exists(f"dll/neko_msgbox{dll_arch}.dll"):
    neko_msgbox = ctypes.CDLL(os.path.abspath(f"dll/neko_msgbox{dll_arch}.dll"))
else:
    print(f"[Error] neko_msgbox{dll_arch}.dll not found!")
    sys.exit(1)

try:
    neko_msgbox.show_msgbox.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    neko_msgbox.show_msgbox.restype = ctypes.c_int
except AttributeError:
    print("[Error] neko_msgbox.show_msgbox function signature is incorrect!")
    sys.exit(1)
except Exception as e:
    print(f"[Error] Failed to set function signature for neko_msgbox: {e}")
    sys.exit(1)

if not os.path.exists(f"dll/neko_winapi{dll_arch}.dll"):
    neko_msgbox.show_msgbox(f"NekoMate - Error".encode("utf-8"), f"neko_winapi{dll_arch}.dll not found!".encode("utf-8"), 0x10)
    sys.exit(1)

if not os.path.exists(f"dll/neko_alpha{dll_arch}.dll"):
    neko_msgbox.show_msgbox(f"NekoMate - Error".encode("utf-8"), f"neko_alpha{dll_arch}.dll not found!".encode("utf-8"), 0x10)
    sys.exit(1)

try:
    neko_api = ctypes.WinDLL(os.path.abspath(f"dll/neko_winapi{dll_arch}.dll"))
    neko_api.move_window.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    neko_api.move_window.restype = ctypes.c_int

    neko_api.set_always_on_top.argtypes = [ctypes.c_void_p, ctypes.c_int]
    neko_api.set_always_on_top.restype = ctypes.c_int

    neko_api.show_window.argtypes = [ctypes.c_void_p, ctypes.c_int]
    neko_api.show_window.restype = ctypes.c_int

    neko_alpha = ctypes.CDLL(os.path.abspath(f"dll/neko_alpha{dll_arch}.dll"))

    neko_alpha.update_layered_window.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
    neko_alpha.update_layered_window.restype = ctypes.c_int

    neko_alpha.process_pixels_premult_rotate_flip.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),  # input_data
        ctypes.c_int,                    # width
        ctypes.c_int,                    # height
        ctypes.POINTER(ctypes.c_uint8)  # output_data
    ]
    neko_alpha.process_pixels_premult_rotate_flip.restype = None
except AttributeError:
    neko_msgbox.show_msgbox(f"NekoMate - Error".encode("utf-8"), f"Failed to set function signatures for DLLs!".encode("utf-8"), 0x10)
    sys.exit(1)
except Exception as e:
    neko_msgbox.show_msgbox(f"NekoMate - Error".encode("utf-8"), f"Failed to load DLLs: {e}".encode("utf-8"), 0x10)
    sys.exit(1)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 128, 128
FPS = 60
DEFAULT_ANIM_FPS = 8
SPRITE_SIZE = 128
STATE_FILE = "neko_state.json"
TRAY_ICON_PATH = "assets/icon.png"

# Default state dict
state_json = {
    "mood": "idle",
    "pos": [100, 100],  # Default position
    "fps": DEFAULT_ANIM_FPS,
}

STATES = {
    "idle": "assets/sprites/neko_idle.png",
    "happy": "assets/sprites/neko_happy.png",
    "sad": "assets/sprites/neko_sad.png",
    "angry": "assets/sprites/neko_angry.png"
}

# Load or create state safely
try:
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump(state_json, f, indent=4)
    with open(STATE_FILE) as f:
        loaded_state = json.load(f)
        state_json.update(loaded_state)
except Exception as e:
    print(f"[Warning] Failed to load state file: {e}")
    # Use defaults if error

mood = state_json.get("mood", "idle")
pos = state_json.get("pos", [100, 100])
ANIM_FPS = state_json.get("fps", DEFAULT_ANIM_FPS)

sprite_path = STATES.get(mood, STATES["idle"])

# Init pygame
pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("NekoMate")
pygame.display.set_icon(pygame.Surface((1, 1)))

# Window handle
hwnd = pygame.display.get_wm_info()["window"] if sys.platform == "win32" else None

if hwnd:
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    # Add WS_EX_APPWINDOW style to show in taskbar
    ex_style |= win32con.WS_EX_APPWINDOW
    # Remove WS_EX_TOOLWINDOW so it appears in taskbar
    ex_style &= ~win32con.WS_EX_TOOLWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, pos[0], pos[1], SCREEN_WIDTH, SCREEN_HEIGHT, win32con.SWP_NOACTIVATE)

# Set window position before creating window (Windows-only)
if sys.platform == "win32":
    try:
        # hide window
        res = neko_api.show_window(hwnd, win32con.SW_HIDE)
        if res == 0:
            print("[Warning] neko_api.show_window failed to hide")
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
        neko_api.show_window(hwnd, win32con.SW_SHOW)
        res = neko_api.show_window(hwnd, win32con.SW_SHOW)
        if res == 0:
            print("[Warning] neko_api.show_window failed to show")
    except Exception as e:
        print(f"[Warning] Failed to modify window style: {e}")

def set_always_on_top(enable: bool):
    global always_on_top
    always_on_top = enable
    if hwnd:
        try:
            # 1 to enable, 0 to disable
            res = neko_api.set_always_on_top(hwnd, 1 if enable else 0)
            if res == 0:
                print("[Warning] neko_api.set_always_on_top failed")
        except Exception as e:
            print(f"[Warning] Failed to set always on top via neko_api: {e}")


if sys.platform == "win32":
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    except Exception as e:
        print(f"[Warning] Failed to modify window style: {e}")
    try:
        SCREEN_WIDTH_MON = ctypes.windll.user32.GetSystemMetrics(0)
        SCREEN_HEIGHT_MON = ctypes.windll.user32.GetSystemMetrics(1)
    except Exception as e:
        print(f"[Warning] Failed to get screen resolution: {e}")
        SCREEN_WIDTH_MON = 1920
        SCREEN_HEIGHT_MON = 1080
else:
    SCREEN_WIDTH_MON = 1920
    SCREEN_HEIGHT_MON = 1080

always_on_top = True
set_always_on_top(always_on_top)

# Load sprite frames safely
try:
    sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
except Exception as e:
    print(f"[Error] Failed to load sprite sheet '{sprite_path}': {e}")
    pygame.quit()
    sys.exit(1)

sheet_width = sprite_sheet.get_width()
SPRITE_FRAMES = sheet_width // SPRITE_SIZE
frames = [sprite_sheet.subsurface((i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
          for i in range(SPRITE_FRAMES)]

# Ensure frames are loaded correctly
if not frames:
    print(f"[Error] No frames loaded from sprite sheet '{sprite_path}'")
    pygame.quit()
    sys.exit(1)

# === Helper functions ===

def move_window(x, y):
    if hwnd:
        max_x = SCREEN_WIDTH_MON - SCREEN_WIDTH
        max_y = SCREEN_HEIGHT_MON - SCREEN_HEIGHT
        clamped_x = max(0, min(x, max_x))
        clamped_y = max(0, min(y, max_y))
        try:
            res = neko_api.move_window(hwnd, clamped_x, clamped_y)
            if res == 0:
                print("[Warning] neko_api.move_window failed")
        except Exception as e:
            print(f"[Warning] Failed to move window via neko_api: {e}")

def get_window_pos():
    if hwnd:
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return rect[0], rect[1]
        except Exception as e:
            print(f"[Warning] Failed to get window position: {e}")
    return 0, 0

def play_sound(path):
    try:
        pygame.mixer.Sound(path).play()
    except Exception as e:
        print(f"[Warning] Error playing sound: {e}")

def on_click():
    print("Neko got clicked! owo")
    # play_sound("assets/sounds/meow.wav")

def get_global_mouse_pos():
    if sys.platform == "win32":
        try:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception as e:
            print(f"[Warning] Failed to get global mouse pos: {e}")
            return 0, 0
    else:
        # fallback: pygame mouse pos relative to window (less accurate)
        return pygame.mouse.get_pos()

# === Tray logic ===

def quit_app(icon, item):
    global running
    running = False
    icon.stop()

def toggle_always_on_top(icon, item):
    set_always_on_top(not always_on_top)
    icon.visible = False
    icon.stop()
    threading.Thread(target=run_tray, daemon=True).start()

def run_tray():
    try:
        image = Image.open(TRAY_ICON_PATH)
        menu = pystray.Menu(
            pystray.MenuItem(
                "Always on Top",
                toggle_always_on_top,
                checked=lambda item: always_on_top
            ),
            pystray.MenuItem("Exit", quit_app)
        )
        icon = pystray.Icon("nekotray", image, "NekoMate", menu)
        icon.run()
    except Exception as e:
        print(f"[Warning] Tray icon failed: {e}")

threading.Thread(target=run_tray, daemon=True).start()

# === Drag & Drop movement vars ===
dragging = False
drag_offset_x = 0
drag_offset_y = 0

clock = pygame.time.Clock()
frame_idx = 0
running = True

ANIM_DELAY = 1.0 / ANIM_FPS
accum_time = 0.0

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    global running
    print("\n[Info] Keyboard interrupt detected, quitting...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

while running:
    dt = clock.tick(FPS) / 1000.0  # delta time in seconds, cap FPS
    accum_time += dt

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                mouse_x, mouse_y = get_global_mouse_pos()
                win_x, win_y = get_window_pos()
                drag_offset_x = mouse_x - win_x
                drag_offset_y = mouse_y - win_y
                on_click()

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                state_json["pos"] = list(get_window_pos())

    if dragging:
        mouse_x, mouse_y = get_global_mouse_pos()
        new_x = mouse_x - drag_offset_x
        new_y = mouse_y - drag_offset_y
        move_window(new_x, new_y)

    # Update animation frame every 1 / ANIM_FPS seconds
    if accum_time >= ANIM_DELAY:
        frame_idx = (frame_idx + 1) % SPRITE_FRAMES
        accum_time -= ANIM_DELAY

    frame_surface = pygame.transform.scale(frames[frame_idx], (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame_surface.fill((0, 0, 0, 0))
    frame_surface.blit(frames[frame_idx], (0, 0))

    if not hwnd or hwnd == 0:
        print("[Error] Invalid window handle!")

    # Prepare input for DLL
    arr = pygame.surfarray.pixels3d(frame_surface).copy()
    alpha = pygame.surfarray.pixels_alpha(frame_surface).copy()

    # Create input RGBA buffer (just regular order)
    input_img = np.empty((SCREEN_HEIGHT, SCREEN_WIDTH, 4), dtype=np.uint8)
    input_img[:, :, 0] = arr[:, :, 2]  # R channel goes to input_img blue (B)
    input_img[:, :, 1] = arr[:, :, 1]  # G channel same
    input_img[:, :, 2] = arr[:, :, 0]  # B channel goes to input_img red (R)
    input_img[:, :, 3] = alpha  # A channel same

    input_flat = input_img.flatten()
    input_ptr = input_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

    # Prepare output buffer for rotated/flipped BGRA data
    output_img = np.empty((SCREEN_WIDTH, SCREEN_HEIGHT, 4), dtype=np.uint8)  # swapped dims for rotate
    output_flat = output_img.flatten()
    output_ptr = output_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

    # Call your DLL function
    result = neko_alpha.process_pixels_premult_rotate_flip(input_ptr, SCREEN_WIDTH, SCREEN_HEIGHT, output_ptr)
    if result == 0:
        print("[Warning] process_pixels_premult_rotate_flip failed")

    frame_data = output_flat.tobytes()

    frame_bytes = (ctypes.c_ubyte * len(frame_data)).from_buffer_copy(frame_data)

    result = neko_alpha.update_layered_window(hwnd, frame_bytes, SCREEN_WIDTH, SCREEN_HEIGHT)
    if result == 0:
        print("[Warning] update_layered_window failed")

    pygame.display.update()

pygame.display.quit()

# Save state on exit (pos, mood, fps)
state_json["fps"] = ANIM_FPS
try:
    with open(STATE_FILE, "w") as f:
        json.dump(state_json, f, indent=4)
except Exception as e:
    print(f"[Warning] Failed to save state file: {e}")

pygame.quit()
