import pygame
import sys
import time

# --- Constants ---
SPRITE_SIZE = 128  # adjust to your actual size
FPS = 5           # how fast to cycle through frames

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((SPRITE_SIZE, SPRITE_SIZE))
clock = pygame.time.Clock()

# --- Load sprite sheet ---
sprite_path = "assets/sprites/neko_idle.png"
sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
sheet_width = sprite_sheet.get_width()
SPRITE_FRAMES = sheet_width // SPRITE_SIZE

frames = [
    sprite_sheet.subsurface((i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)).copy()
    for i in range(SPRITE_FRAMES)
]

if not frames:
    print(f"[Error] No frames loaded from sprite sheet '{sprite_path}'")
    pygame.quit()
    sys.exit(1)

# --- Main Loop ---
frame_index = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    screen.blit(frames[frame_index], (0, 0))
    pygame.display.flip()

    frame_index = (frame_index + 1) % len(frames)
    clock.tick(FPS)

pygame.quit()
