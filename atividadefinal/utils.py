import pygame
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build_path(rel_path):
    return os.path.join(BASE_DIR, rel_path)

def load_png(path):
    full = build_path(path)
    try:
        return pygame.image.load(full).convert_alpha()
    except Exception as e:
        print(f"[ERRO] Falha ao carregar imagem: {full}")
        raise

def load_spritesheet(path, frame_width, frame_height):
    sheet = load_png(path)
    sheet_width, sheet_height = sheet.get_size()

    if sheet_width % frame_width != 0 or sheet_height % frame_height != 0:
        print(f"[AVISO] spritesheet {path} com dimensões incomuns: {sheet_width}x{sheet_height} para frame {frame_width}x{frame_height}")

    frames = []
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = sheet.subsurface((x, y, frame_width, frame_height)).copy()
            frames.append(frame)

    return frames