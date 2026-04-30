# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:05:32 2026 | Creado en Jueves 23 de Abril de 2026
a las 15:05:32 horas
@author: AXMAN y Gemini
"""

import pygame
import math
import sys

# --- Constantes y Configuración | Constants and Configuration ---
# Ancho y alto de la ventana | Window width and height
ANCHO, ALTO = 800, 800 # WIDTH, HEIGHT
# Grosor de la línea y radio del círculo | Line thickness and circle radius
GROSOR_LINEA = 40 # LINE_THICKNESS
RADIO_CIRCULO = 40 # CIRCLE_RADIUS

# Área restringida para el dibujo y análisis de color | Restricted area for drawing and color analysis
LIMITE_MIN_X, LIMITE_MAX_X = 80, 720 # BOUND_MIN_X, BOUND_MAX_X
LIMITE_MIN_Y, LIMITE_MAX_Y = 160, 640 # BOUND_MIN_Y, BOUND_MAX_Y

# Colores permitidos | Allowed colors
NEGRO = (0, 0, 0) # BLACK
NARANJA = (230, 159, 0) # ORANGE
AZUL = (0, 114, 178) # BLUE

# Posiciones de los círculos (dentro del área delimitada) | Circle positions (within bounded area)
POSICIONES_CIRCULOS = [[260, 360], [520, 360], [200, 520], [600, 520]] # CIRCLE_POSITIONS

# Inicializar Pygame | Initialize Pygame
pygame.init()
# Pantalla de visualización | Display screen
pantalla = pygame.display.set_mode((ANCHO, ALTO)) # screen
pygame.display.set_caption("Tarea 1 - Rompecabezas Divergente | Task 1 - Divergent Puzzle")

# Estado del juego | Game state
lineas = []  # Lista para almacenar líneas como diccionarios | List to store lines as dictionaries (lines)
color_actual = NEGRO # current_color
dibujando = False # drawing
pos_inicio = None # start_pos
pos_raton = None # mouse_pos

# --- Funciones Matemáticas y Espaciales | Mathematical and Spatial Functions ---

def limitar_punto(px, py): # clamp_point
    """Restringe una coordenada a los límites del área definida. | Restricts a coordinate to the defined area boundaries."""
    # Calcula x e y dentro de los límites | Calculates x and y within bounds
    x = max(LIMITE_MIN_X, min(px, LIMITE_MAX_X))
    y = max(LIMITE_MIN_Y, min(py, LIMITE_MAX_Y))
    return (x, y)

def distancia_punto_linea(px, py, x1, y1, x2, y2): # point_line_distance
    """Calcula la distancia más corta de un punto a un segmento. | Calculates the shortest distance from a point to a segment."""
    # Magnitud de la línea | Line magnitude
    mag_linea = math.hypot(x2 - x1, y2 - y1) # line_mag
    if mag_linea == 0:
        return math.hypot(px - x1, py - y1)
    
    # Proyección del punto sobre la línea (normalizada) | Point projection over line (normalized)
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (mag_linea ** 2)
    
    if u < 0.0 or u > 1.0:
        # El punto más cercano es uno de los extremos | Closest point is one of the endpoints
        ix, iy = (x1, y1) if u < 0.0 else (x2, y2)
        return math.hypot(px - ix, py - iy)
    
    # El punto más cercano está en el segmento | Closest point is on the segment
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return math.hypot(px - ix, py - iy)

def verificar_interseccion(pos_circulo, linea): # check_intersection
    """Verifica si una línea atraviesa un círculo. | Checks if a line crosses through a circle."""
    # Coordenadas del círculo y la línea | Circle and line coordinates
    cx, cy = pos_circulo
    x1, y1 = linea['inicio'] # start
    x2, y2 = linea['fin'] # end
    
    # Distancia entre punto y línea | Distance between point and line
    dist = distancia_punto_linea(cx, cy, x1, y1, x2, y2)
    # Radio + mitad del grosor de línea | Radius + half of line thickness
    return dist < (RADIO_CIRCULO + GROSOR_LINEA / 2)

# --- Funciones de Dibujo | Drawing Functions ---

def dibujar_simbolo_diamante(superficie, x, y, tamano=12): # draw_diamond_symbol
    """Dibuja un símbolo dividido en 4 cuartos. | Draws a symbol divided into 4 quarters."""
    centro = (x, y) # center
    arriba = (x, y - tamano) # top
    abajo = (x, y + tamano) # bottom
    izquierda = (x - tamano, y) # left
    derecha = (x + tamano, y) # right
    
    # Dibujar polígonos y líneas del diamante | Draw diamond polygons and lines
    pygame.draw.polygon(superficie, NEGRO, [centro, arriba, derecha])
    pygame.draw.polygon(superficie, AZUL, [centro, derecha, abajo])
    pygame.draw.polygon(superficie, NEGRO, [centro, abajo, izquierda])
    pygame.draw.polygon(superficie, AZUL, [centro, izquierda, arriba])
    
    pygame.draw.line(superficie, NARANJA, arriba, abajo, 2)
    pygame.draw.line(superficie, NARANJA, izquierda, derecha, 2)

def dibujar_indicadores(): # draw_indicators
    """Dibuja los 3 indicadores solicitados. | Draws the 3 requested indicators."""
    # 1. Conteo de Líneas (Inicia en 4) | Line Count (Starts at 4)
    conteo_lineas_validas = sum(1 for linea in lineas if linea['color'] in [NEGRO, AZUL]) # valid_lines_count
    indicador_lineas = max(0, 4 - conteo_lineas_validas) # lines_indicator
    
    # 2. Cantidad de colores presentes | Amount of colors present
    colores_presentes = {NARANJA, AZUL} # colors_present
    for linea in lineas:
        colores_presentes.add(linea['color'])
    indicador_color = len(colores_presentes) # color_indicator
    
    # 3. Cantidad de Círculos Visibles | Visible Circles Count
    circulos_visibles = 4 # visible_circles
    for circulo in POSICIONES_CIRCULOS:
        for linea in lineas:
            if linea['color'] in [NEGRO, AZUL] and verificar_interseccion(circulo, linea):
                circulos_visibles -= 1
                break 
    
    # Renderizado de indicadores en pantalla | Rendering indicators on screen
    pygame.draw.line(pantalla, NEGRO, (15, 20), (35, 20), 4)
    for i in range(indicador_lineas):
        dibujar_simbolo_diamante(pantalla, 60 + (i * 30), 20)
        
    pygame.draw.circle(pantalla, NEGRO, (20, 50), 4)
    pygame.draw.circle(pantalla, AZUL, (30, 50), 4)
    for i in range(indicador_color):
        dibujar_simbolo_diamante(pantalla, 60 + (i * 30), 50)
        
    pygame.draw.circle(pantalla, AZUL, (25, 80), 8, 2)
    for i in range(circulos_visibles):
        dibujar_simbolo_diamante(pantalla, 60 + (i * 30), 80)

def dibujar_interfaz(): # draw_ui
    """Dibuja la interfaz de paleta de colores. | Draws the color palette interface."""
    # Botones de color | Color buttons
    pygame.draw.rect(pantalla, NEGRO, (650, 20, 40, 40))
    pygame.draw.rect(pantalla, NARANJA, (700, 20, 40, 40))
    pygame.draw.rect(pantalla, AZUL, (750, 20, 40, 40))
    
    # Resaltar color seleccionado | Highlight selected color
    if color_actual == NEGRO:
        pygame.draw.rect(pantalla, AZUL, (648, 18, 44, 44), 3)
    elif color_actual == NARANJA:
        pygame.draw.rect(pantalla, NEGRO, (698, 18, 44, 44), 3)
    elif color_actual == AZUL:
        pygame.draw.rect(pantalla, NEGRO, (748, 18, 44, 44), 3)

# --- Bucle Principal | Main Loop ---
reloj = pygame.time.Clock() # clock
ejecutando = True # running

while ejecutando:
    # Obtener posición cruda del ratón | Get raw mouse position
    pos_raton_cruda = pygame.mouse.get_pos() # raw_mouse_pos
    
    for evento in pygame.event.get(): # event
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_q: 
                ejecutando = False
            elif evento.key == pygame.K_r: # Reiniciar juego | Reset game
                lineas.clear()
                
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Click izquierdo | Left click
                # Interacción con Paleta de Colores | Color Palette interaction
                if 20 <= pos_raton_cruda[1] <= 60:
                    if 650 <= pos_raton_cruda[0] <= 690:
                        color_actual = NEGRO
                        continue
                    elif 700 <= pos_raton_cruda[0] <= 740:
                        color_actual = NARANJA
                        continue
                    elif 750 <= pos_raton_cruda[0] <= 790:
                        color_actual = AZUL
                        continue
                
                # Iniciar dibujo | Start drawing
                dibujando = True
                pos_inicio = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1])
                
            elif evento.button == 3: # Click derecho / Borrador | Right click / Eraser
                lineas_a_eliminar = [] # lines_to_remove
                for linea in lineas:
                    dist = distancia_punto_linea(pos_raton_cruda[0], pos_raton_cruda[1], linea['inicio'][0], linea['inicio'][1], linea['fin'][0], linea['fin'][1])
                    if dist <= GROSOR_LINEA / 2:
                        lineas_a_eliminar.append(linea)
                        break 
                
                for linea in lineas_a_eliminar:
                    lineas.remove(linea)
                    
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1 and dibujando:
                dibujando = False
                pos_fin = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1]) # end_pos
                
                if pos_inicio != pos_fin:
                    lineas.append({'inicio': pos_inicio, 'fin': pos_fin, 'color': color_actual})

    # --- Renderizado | Rendering ---
    pantalla.fill(NARANJA) 
    
    # Dibujar círculos de fondo | Draw background circles
    for pos in POSICIONES_CIRCULOS:
        pygame.draw.circle(pantalla, AZUL, pos, RADIO_CIRCULO)
        
    # Dibujar líneas existentes | Draw existing lines
    for linea in lineas:
        pygame.draw.line(pantalla, linea['color'], linea['inicio'], linea['fin'], GROSOR_LINEA)
        pygame.draw.circle(pantalla, linea['color'], linea['inicio'], GROSOR_LINEA // 2)
        pygame.draw.circle(pantalla, linea['color'], linea['fin'], GROSOR_LINEA // 2)
        
    # Dibujar línea activa mientras se arrastra | Draw active line while dragging
    if dibujando:
        raton_limitado = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1]) # clamped_mouse
        pygame.draw.line(pantalla, color_actual, pos_inicio, raton_limitado, GROSOR_LINEA)
        pygame.draw.circle(pantalla, color_actual, pos_inicio, GROSOR_LINEA // 2)
        pygame.draw.circle(pantalla, color_actual, raton_limitado, GROSOR_LINEA // 2)

    # Dibujar Interfaz e Indicadores | Draw UI and Indicators
    dibujar_interfaz()
    dibujar_indicadores()

    # Actualizar pantalla | Update display
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()