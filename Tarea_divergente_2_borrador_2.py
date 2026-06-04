# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 22:05:43 2026

@author: AXMAN
"""

# -*- coding: utf-8 -*-
"""
Tarea Divergente 2 - Espacio de Soluciones Continuo y Propiedades Mutables
"""

import pygame
import sys
import math
import random

# Inicialización
pygame.init()
WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tarea Divergente 2 - Lienzo Libre y Agrupación")

# Paleta Okabe-Ito estricta (Accesibilidad)
OKABE_ITO = [
    (230, 159, 0),   # Naranja
    (86, 180, 233),  # Azul cielo
    (0, 158, 115),   # Verde azulado
    (240, 228, 66),  # Amarillo
    (213, 94, 0)     # Bermellón
]
COLOR_BASE_GRANDE = (150, 150, 150)
COLOR_FONDO = (25, 25, 25)
COLOR_ROMBO_OFF = (50, 50, 50)
COLOR_ROMBO_ON = (230, 159, 0) # Naranja Okabe-Ito

# Constantes de objetos
SHAPE_RADIUS = 40
CLUSTER_DISTANCE = 90 # Distancia para considerar que dos piezas están "conectadas"

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
    r = size
    offset = math.radians(rotation_angle) - math.pi/2 
    
    if shape_type == 0: # Círculo (agregamos una pequeña línea para notar la rotación)
        pygame.draw.circle(surface, color, center, r)
        end_x = center[0] + r * math.cos(offset)
        end_y = center[1] + r * math.sin(offset)
        pygame.draw.line(surface, (0,0,0), center, (end_x, end_y), 3)
    elif shape_type == 1: # Triángulo
        draw_regular_polygon(surface, color, center, r, 3, offset)
    elif shape_type == 2: # Estrella 4 puntas
        draw_star(surface, color, center, r, r//2.5, 4, offset)
    elif shape_type == 3: # Pentágono
        draw_regular_polygon(surface, color, center, r, 5, offset)
    elif shape_type == 4: # Estrella 5 puntas
        draw_star(surface, color, center, r, r//2.5, 5, offset)

class FloatingObject:
    def __init__(self, x, y, large_shape, small_shape, color_idx):
        self.x = x
        self.y = y
        self.large_shape = large_shape
        self.small_shape = small_shape
        self.color_idx = color_idx
        self.rotation = random.choice([0, 90, 180, 270])

    def draw(self, surface):
        center = (int(self.x), int(self.y))
        draw_shape(surface, COLOR_BASE_GRANDE, self.large_shape, center, SHAPE_RADIUS, self.rotation)
        color = OKABE_ITO[self.color_idx]
        draw_shape(surface, color, self.small_shape, center, SHAPE_RADIUS // 2, self.rotation)

def generate_random_pieces(count=25):
    pieces = []
    for _ in range(count):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        large_shape = random.randint(0, 4)
        small_shape = random.randint(0, 4)
        color_idx = random.randint(0, 4)
        pieces.append(FloatingObject(x, y, large_shape, small_shape, color_idx))
    return pieces

def get_clusters(pieces):
    # Encontrar componentes conectados basados en distancia física
    clusters = []
    visited = set()
    
    for i, p1 in enumerate(pieces):
        if i not in visited:
            cluster = [i]
            visited.add(i)
            queue = [i]
            
            while queue:
                curr = queue.pop(0)
                for j, p2 in enumerate(pieces):
                    if j not in visited:
                        dist = math.hypot(pieces[curr].x - p2.x, pieces[curr].y - p2.y)
                        if dist < CLUSTER_DISTANCE:
                            visited.add(j)
                            cluster.append(j)
                            queue.append(j)
            clusters.append(cluster)
    return clusters

def evaluate_board(pieces):
    clusters = get_clusters(pieces)
    
    espacial_score = 0
    relacional_score = 0
    cuantitativo_score = 0
    
    # Evaluar la calidad de los clusters (agrupaciones de 3 o más piezas)
    for cluster_indices in clusters:
        if len(cluster_indices) >= 3:
            cluster_pieces = [pieces[i] for i in cluster_indices]
            
            # Criterio 1: Espacial (Agrupación por forma grande idéntica)
            if len(set(p.large_shape for p in cluster_pieces)) == 1:
                espacial_score += len(cluster_pieces)
                
                # Criterio 2: Relacional (Mismo color de elemento pequeño en el cluster válido)
                if len(set(p.color_idx for p in cluster_pieces)) == 1:
                    relacional_score += len(cluster_pieces)
                    
                # Criterio 3: Cuantitativo/Orientación (Mis ángulo de rotación en el cluster válido)
                if len(set(p.rotation for p in cluster_pieces)) == 1:
                    cuantitativo_score += len(cluster_pieces)
                    
    # Normalizar a máximos de 25
    return espacial_score, relacional_score, cuantitativo_score

def draw_hud(surface, scores, total_pieces=25):
    start_x = 20
    start_y = 20
    spacing_y = 50
    
    # Criterio 1 (Espacial): Triángulo
    # Criterio 2 (Relacional): Círculo
    # Criterio 3 (Cuantitativo): Cuadrado
    symbols = [(1, 3), (0, 0), (1, 4)] 
    
    for i, score in enumerate(scores):
        cluster_y = start_y + i * spacing_y
        
        # Símbolo identificador
        if symbols[i][0] == 0:
            pygame.draw.circle(surface, (150,150,150), (start_x + 15, cluster_y + 15), 12)
        else:
            draw_regular_polygon(surface, (150,150,150), (start_x + 15, cluster_y + 15), 15, symbols[i][1])
            
        # Rombos de Zelda (5 rombos como máximo visual, representando 5 puntos cada uno)
        num_rombos_activos = score // 5
        residuo = score % 5
        
        for j in range(5):
            rx = start_x + 50 + j * 30
            ry = cluster_y + 15
            color = COLOR_ROMBO_ON if j < num_rombos_activos else COLOR_ROMBO_OFF
            draw_regular_polygon(surface, color, (rx, ry), 10, 4)

def main():
    clock = pygame.time.Clock()
    pieces = generate_random_pieces()
    
    dragging_idx = None
    mouse_offset_x = 0
    mouse_offset_y = 0

    # Variables internas matemáticas
    total_criterios_C = 75 # 25 por cada uno de los 3 criterios posibles

    running = True
    while running:
        screen.fill(COLOR_FONDO)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # Salir
                    running = False
                elif event.key == pygame.K_r: # Reiniciar
                    pieces = generate_random_pieces()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Buscar si se hizo clic en una pieza (de arriba hacia abajo para seleccionar la superior)
                for i in reversed(range(len(pieces))):
                    dist = math.hypot(mouse_x - pieces[i].x, mouse_y - pieces[i].y)
                    if dist <= SHAPE_RADIUS:
                        if event.button == 1: # Click izquierdo para arrastrar
                            dragging_idx = i
                            mouse_offset_x = pieces[i].x - mouse_x
                            mouse_offset_y = pieces[i].y - mouse_y
                            # Traer al frente
                            pieces.append(pieces.pop(i))
                            dragging_idx = len(pieces) - 1
                            break
                        elif event.button == 3: # Click derecho para mutar (Descubrimiento por manipulación)
                            pieces[i].color_idx = (pieces[i].color_idx + 1) % 5
                            pieces[i].rotation = (pieces[i].rotation + 90) % 360
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_idx = None

        if dragging_idx is not None:
            pieces[dragging_idx].x = mouse_x + mouse_offset_x
            pieces[dragging_idx].y = mouse_y + mouse_offset_y

        # Dibujar líneas de conexión tenues para insinuar el concepto espacial de agrupamiento
        clusters = get_clusters(pieces)
        for cluster in clusters:
            if len(cluster) >= 2:
                for i in range(len(cluster)):
                    for j in range(i + 1, len(cluster)):
                        p1 = pieces[cluster[i]]
                        p2 = pieces[cluster[j]]
                        if math.hypot(p1.x - p2.x, p1.y - p2.y) < CLUSTER_DISTANCE:
                            pygame.draw.line(screen, (50, 50, 50), (p1.x, p1.y), (p2.x, p2.y), 2)

        # Dibujar objetos
        for p in pieces:
            p.draw(screen)

        # Evaluar y mostrar HUD simbólico
        scores = evaluate_board(pieces)
        draw_hud(screen, scores)

        # VARIABLE INTERNA: Ecuación Lineal de Divergencia
        criterios_activados_X = sum(scores)
        calidad_de_respuesta = (criterios_activados_X / total_criterios_C) * 100
        
        # Imprime discretamente en consola la calidad sin romper la ambigüedad en pantalla
        print(f"Calidad de Respuesta Lineal (Cr): {calidad_de_respuesta:.2f}")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()