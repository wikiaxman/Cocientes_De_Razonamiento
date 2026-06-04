# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 19:26:17 2026

@author: AXMAN
"""

import pygame
import sys
import math
import random

# Inicialización
pygame.init()
WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tarea Divergente 2 - Convergencia Espacial y Relacional")

# Paleta Okabe-Ito para elementos pequeños
OKABE_ITO = [
    (230, 159, 0),   # Naranja
    (86, 180, 233),  # Azul cielo
    (0, 158, 115),   # Verde azulado
    (240, 228, 66),  # Amarillo
    (213, 94, 0)     # Bermellón
]
COLOR_BASE_GRANDE = (150, 150, 150) # Todos los elementos grandes del mismo color
COLOR_FONDO = (25, 25, 25)
COLOR_ROMBO_OFF = (50, 50, 50)
COLOR_ROMBO_ON = (0, 114, 178) # Azul Okabe-Ito para retroalimentación

# Constantes de cuadrícula
GRID_SIZE = 500
CELL_SIZE = 100
GRID_COLS = 5
GRID_ROWS = 5
START_X = (WIDTH - GRID_SIZE) // 2
START_Y = (HEIGHT - GRID_SIZE) // 2

# Funciones de dibujo geométrico
def draw_regular_polygon(surface, color, center, radius, num_sides, angle_offset=0):
    points = []
    for i in range(num_sides):
        angle = angle_offset + i * (2 * math.pi / num_sides)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)

def draw_star(surface, color, center, outer_radius, inner_radius, num_points, angle_offset=0):
    points = []
    angle_step = math.pi / num_points
    for i in range(2 * num_points):
        r = outer_radius if i % 2 == 0 else inner_radius
        angle = angle_offset + i * angle_step
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)

def draw_shape(surface, color, shape_type, center, size, rotation_angle=0):
    r = size // 2
    offset = math.radians(rotation_angle) - math.pi/2 # Empezar apuntando arriba
    
    if shape_type == 0: # Círculo
        pygame.draw.circle(surface, color, center, r)
    elif shape_type == 1: # Triángulo
        draw_regular_polygon(surface, color, center, r, 3, offset)
    elif shape_type == 2: # Estrella 4 puntas
        draw_star(surface, color, center, r, r//2.5, 4, offset)
    elif shape_type == 3: # Pentágono
        draw_regular_polygon(surface, color, center, r, 5, offset)
    elif shape_type == 4: # Estrella 5 puntas
        draw_star(surface, color, center, r, r//2.5, 5, offset)

class CompositeObject:
    def __init__(self, large_shape, small_shape, color_idx):
        self.large_shape = large_shape
        self.small_shape = small_shape
        self.color_idx = color_idx
        self.color = OKABE_ITO[color_idx]
        self.rotation = 0 # 0, 90, 180, 270

    def draw(self, surface, x, y):
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        # Elemento grande (tamaño completo de la celda con un pequeño margen)
        draw_shape(surface, COLOR_BASE_GRANDE, self.large_shape, center, CELL_SIZE - 20, self.rotation)
        # Elemento pequeño (mitad del tamaño) dibujado en el centro
        draw_shape(surface, self.color, self.small_shape, center, (CELL_SIZE - 20) // 2, self.rotation)

def generate_ideal_grid():
    # Garantiza una solución perfecta generando un cuadrado latino
    grid = []
    for r in range(GRID_ROWS):
        row = []
        for c in range(GRID_COLS):
            # Filas = mismo elemento grande, Columnas = mismo elemento pequeño, Diagonales = colores
            obj = CompositeObject(large_shape=r, small_shape=c, color_idx=(r + c) % 5)
            row.append(obj)
        grid.append(row)
    return grid

def shuffle_grid(grid):
    flat_list = [item for sublist in grid for item in sublist]
    random.shuffle(flat_list)
    for obj in flat_list:
        obj.rotation = random.choice([0, 90, 180, 270]) # Rotación inicial aleatoria
    
    new_grid = []
    idx = 0
    for r in range(GRID_ROWS):
        row = []
        for c in range(GRID_COLS):
            row.append(flat_list[idx])
            idx += 1
        new_grid.append(row)
    return new_grid

def evaluate_grid(grid):
    # Retorna tuplas (actual, máximo) para cada indicador
    
    # 1. Filas/Columnas alineadas por elementos grandes (Max 10)
    grandes_score = 0
    for r in range(GRID_ROWS):
        if len(set(obj.large_shape for obj in grid[r])) == 1: grandes_score += 1
    for c in range(GRID_COLS):
        if len(set(grid[r][c].large_shape for r in range(GRID_ROWS))) == 1: grandes_score += 1

    # 2. Elementos pequeños alineados por forma (Max 10)
    pequenos_score = 0
    for r in range(GRID_ROWS):
        if len(set(obj.small_shape for obj in grid[r])) == 1: pequenos_score += 1
    for c in range(GRID_COLS):
        if len(set(grid[r][c].small_shape for r in range(GRID_ROWS))) == 1: pequenos_score += 1

    # 3. Elementos pequeños alineados por color (Max 10)
    color_score = 0
    for r in range(GRID_ROWS):
        if len(set(obj.color_idx for obj in grid[r])) == 1: color_score += 1
    for c in range(GRID_COLS):
        if len(set(grid[r][c].color_idx for r in range(GRID_ROWS))) == 1: color_score += 1

    # 4. NUEVO: Orientación Constante (Max 5) - Todos los objetos de una misma forma grande miran al mismo lado
    orientacion_score = 0
    for shape_type in range(5):
        rotations = [grid[r][c].rotation for r in range(GRID_ROWS) for c in range(GRID_COLS) if grid[r][c].large_shape == shape_type]
        if len(rotations) == 5 and len(set(rotations)) == 1:
            orientacion_score += 1

    # 5. NUEVO: Patrón de Cuadrado Latino de Colores (Max 5) - Evita contar colores agrupados, premia dispersión diagonal
    latino_score = 0
    for diag_offset in range(5):
        diag_colors = [grid[i][(i + diag_offset) % 5].color_idx for i in range(5)]
        if len(set(diag_colors)) == 1: latino_score += 1

    return [
        (grandes_score, 10),
        (pequenos_score, 10),
        (color_score, 10),
        (orientacion_score, 5),
        (latino_score, 5)
    ]

def draw_hud(surface, scores):
    # Estilo "Leyenda de Zelda", indicadores abstractos sin números ni letras
    start_x = 20
    start_y = 20
    spacing_y = 60
    
    for i, (current, maximum) in enumerate(scores):
        cluster_y = start_y + i * spacing_y
        
        # Dibujar forma base del indicador para diferenciar qué mide cada uno
        draw_regular_polygon(surface, (100,100,100), (start_x + 20, cluster_y + 15), 15, i+3) 
        
        # Dibujar rombos de progreso (proporcional al máximo)
        rombo_spacing = 25
        num_rombos = 5 # Normalizamos visualmente a 5 rombos por categoría para no saturar la pantalla
        progreso_normalizado = (current / maximum) * num_rombos if maximum > 0 else 0
        
        for j in range(num_rombos):
            rx = start_x + 60 + j * rombo_spacing
            ry = cluster_y + 15
            color = COLOR_ROMBO_ON if j < progreso_normalizado else COLOR_ROMBO_OFF
            draw_regular_polygon(surface, color, (rx, ry), 8, 4)

def main():
    clock = pygame.time.Clock()
    ideal_grid = generate_ideal_grid()
    grid = shuffle_grid(ideal_grid)
    
    dragging = False
    dragged_obj = None
    dragged_origin = None # (row, col)
    mouse_offset_x = 0
    mouse_offset_y = 0

    running = True
    while running:
        screen.fill(COLOR_FONDO)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    grid = shuffle_grid(ideal_grid)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Click izquierdo para arrastrar
                    col = (mouse_x - START_X) // CELL_SIZE
                    row = (mouse_y - START_Y) // CELL_SIZE
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                        dragging = True
                        dragged_obj = grid[row][col]
                        dragged_origin = (row, col)
                        mouse_offset_x = mouse_x - (START_X + col * CELL_SIZE)
                        mouse_offset_y = mouse_y - (START_Y + row * CELL_SIZE)
                
                elif event.button == 3: # Click derecho para rotar (NUEVA MECÁNICA)
                    col = (mouse_x - START_X) // CELL_SIZE
                    row = (mouse_y - START_Y) // CELL_SIZE
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                        grid[row][col].rotation = (grid[row][col].rotation + 90) % 360

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    col = (mouse_x - START_X) // CELL_SIZE
                    row = (mouse_y - START_Y) // CELL_SIZE
                    
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                        # Intercambiar posiciones
                        orig_row, orig_col = dragged_origin
                        grid[orig_row][orig_col] = grid[row][col]
                        grid[row][col] = dragged_obj
                    
                    dragging = False
                    dragged_obj = None

        # Dibujar la cuadrícula y objetos
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rect_x = START_X + c * CELL_SIZE
                rect_y = START_Y + r * CELL_SIZE
                pygame.draw.rect(screen, (40, 40, 40), (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 1)
                
                # No dibujar el objeto si se está arrastrando en este momento
                if dragging and dragged_origin == (r, c):
                    continue
                grid[r][c].draw(screen, rect_x, rect_y)

        # Dibujar el objeto arrastrado por encima de todo
        if dragging and dragged_obj:
            draw_x = mouse_x - mouse_offset_x
            draw_y = mouse_y - mouse_offset_y
            dragged_obj.draw(screen, draw_x, draw_y)

        # Evaluar y dibujar retroalimentación simbólica
        scores = evaluate_grid(grid)
        draw_hud(screen, scores)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()