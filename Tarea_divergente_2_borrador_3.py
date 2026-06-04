# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 23:49:54 2026

@author: AXMAN
"""

# -*- coding: utf-8 -*-
"""
Tarea Divergente 2 - Lienzo Libre y Agrupación (Ajustes Estéticos)
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
CLUSTER_DISTANCE = 110 # Aumentado ligeramente para mejorar la detección de cercanía

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
    
    if shape_type == 0: # Círculo 
        pygame.draw.circle(surface, color, center, r)
    elif shape_type == 1: # Triángulo
        draw_regular_polygon(surface, color, center, r, 3, offset)
    elif shape_type == 2: # Cuadrado (Polígono de 4 lados rotado 45 grados para apoyarse plano)
        square_offset = offset + math.pi/4
        draw_regular_polygon(surface, color, center, r, 4, square_offset)
    elif shape_type == 3: # Estrella 4 puntas
        draw_star(surface, color, center, r, r//2.5, 4, offset)
    elif shape_type == 4: # Pentágono
        draw_regular_polygon(surface, color, center, r, 5, offset)

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
        
        # 1. Dibujar figura grande base
        draw_shape(surface, COLOR_BASE_GRANDE, self.large_shape, center, SHAPE_RADIUS, self.rotation)
        
        # 2. Dibujar figura pequeña interior
        color = OKABE_ITO[self.color_idx]
        draw_shape(surface, color, self.small_shape, center, SHAPE_RADIUS // 2, self.rotation)
        
        # 3. Dibujar la rayita negra indicadora de rotación por encima de todo
        offset = math.radians(self.rotation) - math.pi/2 
        end_x = center[0] + SHAPE_RADIUS * math.cos(offset)
        end_y = center[1] + SHAPE_RADIUS * math.sin(offset)
        pygame.draw.line(surface, (0, 0, 0), center, (end_x, end_y), 3)

def generate_fair_pieces():
    # Garantiza exactamente 5 de cada forma grande para que la solución 100% siempre sea posible
    pieces = []
    large_shapes_deck = [i for i in range(5) for _ in range(5)]
    random.shuffle(large_shapes_deck)
    
    for i in range(25):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        large_shape = large_shapes_deck[i]
        small_shape = random.randint(0, 4)
        color_idx = random.randint(0, 4)
        pieces.append(FloatingObject(x, y, large_shape, small_shape, color_idx))
    return pieces

def get_clusters(pieces):
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
    
    # Evaluamos por cantidad de clústeres válidos (Max 5 puntos por criterio)
    espacial_score = 0
    relacional_score = 0
    cuantitativo_score = 0
    
    for cluster_indices in clusters:
        if len(cluster_indices) >= 3: # Un clúster es válido si tiene 3 o más piezas
            cluster_pieces = [pieces[i] for i in cluster_indices]
            
            # Criterio 1: Espacial (Misma forma grande = 1 rombo)
            if len(set(p.large_shape for p in cluster_pieces)) == 1:
                espacial_score += 1
                
            # Criterio 2: Relacional (Mismo color = 1 rombo)
            if len(set(p.color_idx for p in cluster_pieces)) == 1:
                relacional_score += 1
                
            # Criterio 3: Cuantitativo/Orientación (Misma rotación = 1 rombo)
            if len(set(p.rotation for p in cluster_pieces)) == 1:
                cuantitativo_score += 1
                    
    # Aseguramos que no pase del máximo visual de 5 rombos por categoría
    return min(espacial_score, 5), min(relacional_score, 5), min(cuantitativo_score, 5)

def draw_hud(surface, scores):
    start_x = 20
    start_y = 20
    spacing_y = 50
    
    # Símbolos representativos: Triángulo (Espacial), Círculo (Relacional), Cuadrado (Cuantitativo)
    symbols = [(1, 3), (0, 0), (1, 4)] 
    
    for i, score in enumerate(scores):
        cluster_y = start_y + i * spacing_y
        
        if symbols[i][0] == 0:
            pygame.draw.circle(surface, (150,150,150), (start_x + 15, cluster_y + 15), 12)
        else:
            # Compensar la rotación del cuadrado en el HUD para que se vea plano
            offset = math.pi/4 if symbols[i][1] == 4 else 0
            draw_regular_polygon(surface, (150,150,150), (start_x + 15, cluster_y + 15), 15, symbols[i][1], offset)
            
        for j in range(5):
            rx = start_x + 50 + j * 30
            ry = cluster_y + 15
            color = COLOR_ROMBO_ON if j < score else COLOR_ROMBO_OFF
            draw_regular_polygon(surface, color, (rx, ry), 10, 4)

def main():
    clock = pygame.time.Clock()
    pieces = generate_fair_pieces()
    
    dragging_idx = None
    mouse_offset_x = 0
    mouse_offset_y = 0

    # Total de criterios posibles = 15 (5 clústeres x 3 categorías)
    total_criterios_C = 15 

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
                    pieces = generate_fair_pieces()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in reversed(range(len(pieces))):
                    dist = math.hypot(mouse_x - pieces[i].x, mouse_y - pieces[i].y)
                    if dist <= SHAPE_RADIUS:
                        if event.button == 1: # Clic Izquierdo: Arrastrar
                            dragging_idx = i
                            mouse_offset_x = pieces[i].x - mouse_x
                            mouse_offset_y = pieces[i].y - mouse_y
                            pieces.append(pieces.pop(i)) # Traer al frente
                            dragging_idx = len(pieces) - 1
                            break
                        elif event.button == 3: # Clic Derecho: Cambiar color
                            pieces[i].color_idx = (pieces[i].color_idx + 1) % 5
                            break
                
            elif event.type == pygame.MOUSEWHEEL:
                # Rueda del ratón: Rotación rápida
                for i in reversed(range(len(pieces))):
                    dist = math.hypot(mouse_x - pieces[i].x, mouse_y - pieces[i].y)
                    if dist <= SHAPE_RADIUS:
                        if event.y > 0: # Scroll arriba
                            pieces[i].rotation = (pieces[i].rotation + 90) % 360
                        elif event.y < 0: # Scroll abajo
                            pieces[i].rotation = (pieces[i].rotation - 90) % 360
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_idx = None

        if dragging_idx is not None:
            pieces[dragging_idx].x = mouse_x + mouse_offset_x
            pieces[dragging_idx].y = mouse_y + mouse_offset_y

        # Dibujar red de conexiones
        clusters = get_clusters(pieces)
        for cluster in clusters:
            if len(cluster) >= 2:
                for i in range(len(cluster)):
                    for j in range(i + 1, len(cluster)):
                        p1 = pieces[cluster[i]]
                        p2 = pieces[cluster[j]]
                        if math.hypot(p1.x - p2.x, p1.y - p2.y) < CLUSTER_DISTANCE:
                            # Grosor de la línea aumentado a 4
                            pygame.draw.line(screen, (60, 60, 60), (p1.x, p1.y), (p2.x, p2.y), 4) 

        # Dibujar piezas
        for p in pieces:
            p.draw(screen)

        # HUD y Evaluación
        scores = evaluate_board(pieces)
        draw_hud(screen, scores)

        # Variable interna de calidad lineal solicitada en los lineamientos
        criterios_activados_X = sum(scores)
        calidad_de_respuesta = (criterios_activados_X / total_criterios_C) * 100

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()