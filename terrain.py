"""
Terrain - the temple garden map
Sandy paths that Mara must walk, and raised grass terraces for towers
"""

import math
import random
import pygame
from config import (GRID_COLS, GRID_ROWS, GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,
                   TERRACE_COLOR, PATH_COLOR, CLIFF_COLOR, GATE_COLOR)


def build_path_tiles(paths):
    """Turn each path's corner points into the full set of tiles it covers"""
    tiles = set()
    for path in paths:
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            step_x = (x2 > x1) - (x2 < x1)
            step_y = (y2 > y1) - (y2 < y1)
            x, y = x1, y1
            tiles.add((x, y))
            while (x, y) != (x2, y2):
                x += step_x
                y += step_y
                tiles.add((x, y))
    return tiles


def shade(color, amount):
    """Lighten (positive) or darken (negative) a colour"""
    return tuple(max(0, min(255, c + amount)) for c in color)


def render_terrain(paths, path_tiles):
    """Draw the whole map once onto a surface we can reuse every frame"""
    def is_path(grid_x, grid_y):
        return (grid_x, grid_y) in path_tiles
    
    surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    rng = random.Random(7)  # Fixed seed so the map looks the same every game

    for gy in range(GRID_ROWS):
        for gx in range(GRID_COLS):
            rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if is_path(gx, gy):
                # Sandy path with a few pebbles
                pygame.draw.rect(surface, shade(PATH_COLOR, rng.randint(-6, 6)), rect)
                for _ in range(3):
                    px = rect.x + rng.randint(4, TILE_SIZE - 4)
                    py = rect.y + rng.randint(4, TILE_SIZE - 4)
                    pygame.draw.circle(surface, shade(PATH_COLOR, -35), (px, py), rng.randint(1, 2))
            else:
                # Grass terrace with tufts and the odd flower
                pygame.draw.rect(surface, shade(TERRACE_COLOR, rng.randint(-8, 8)), rect)
                for _ in range(4):
                    tx = rect.x + rng.randint(4, TILE_SIZE - 4)
                    ty = rect.y + rng.randint(4, TILE_SIZE - 4)
                    pygame.draw.line(surface, shade(TERRACE_COLOR, 25), (tx, ty), (tx + 2, ty - 4))
                if rng.random() < 0.12:
                    fx = rect.x + rng.randint(6, TILE_SIZE - 6)
                    fy = rect.y + rng.randint(6, TILE_SIZE - 6)
                    pygame.draw.circle(surface, rng.choice([(240, 200, 220), (250, 240, 170)]), (fx, fy), 2)

                # Faint tile border so building spots are easy to see
                pygame.draw.rect(surface, shade(TERRACE_COLOR, -14), rect, 1)

                # Cliff edges where the terrace drops down to a path
                if is_path(gx, gy + 1):  # Path below - draw the rocky cliff face
                    face = pygame.Rect(rect.x, rect.bottom - 8, TILE_SIZE, 8)
                    pygame.draw.rect(surface, CLIFF_COLOR, face)
                    pygame.draw.line(surface, shade(CLIFF_COLOR, -30), face.topleft, face.topright, 2)
                if is_path(gx, gy - 1):
                    pygame.draw.line(surface, shade(CLIFF_COLOR, -20), rect.topleft, rect.topright, 3)
                if is_path(gx - 1, gy):
                    pygame.draw.line(surface, shade(CLIFF_COLOR, -20), rect.topleft, rect.bottomleft, 3)
                if is_path(gx + 1, gy):
                    pygame.draw.line(surface, shade(CLIFF_COLOR, -20), rect.topright, rect.bottomright, 3)

    # Mara gates where each path starts
    for path in paths:
        gx, gy = path[0]
        cx = gx * TILE_SIZE + TILE_SIZE // 2
        cy = gy * TILE_SIZE + TILE_SIZE // 2
        for radius, amount in ((16, 0), (11, 30), (5, 60)):
            pygame.draw.circle(surface, shade(GATE_COLOR, amount), (cx, cy), radius)

    return surface
