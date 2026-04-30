# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 16:03:08 2026 | Creado en Jueves 23 de Abril de 2026
a las 16:03:08 horas

@author: AXMAN y Gemini
"""

import pygame
import math
import sys

# --- Constantes y Configuración | Constants and Configuration ---
# Ancho y alto de la ventana | Window width and height
ANCHO, ALTO = 800, 800
# Grosor de las líneas dibujadas | Thickness of drawn lines
GROSOR_LINEA = 40
# Radio de los círculos base | Radius of the base circles
RADIO_CIRCULO = 40

# Área restringida para el dibujo y análisis de color | Restricted area for drawing and color analysis
LIMITE_MIN_X, LIMITE_MAX_X = 80, 720
LIMITE_MIN_Y, LIMITE_MAX_Y = 160, 640

# Colores permitidos | Allowed colors
NEGRO = (0, 0, 0)
NARANJA = (230, 159, 0)
AZUL = (0, 114, 178)

# Posiciones de los círculos (dentro del área delimitada) | Positions of the circles (within the bounded area)
POSICIONES_CIRCULOS = [[260, 360], [520, 360], [200, 520], [600, 520]]

# Inicializar Pygame | Initialize Pygame
pygame.init()
# Pantalla principal del juego | Main game screen
pantalla = pygame.display.set_mode((ANCHO, ALTO))
# Título de la ventana | Window title
pygame.display.set_caption("Task 1 - Divergent Puzzle")

# Estado del juego | Game state
# Lista para guardar los trazos de las líneas | List to store the line strokes
lineas = [] 
# Color seleccionado actualmente | Currently selected color
color_actual = NEGRO
# Bandera que indica si el jugador está dibujando | Flag indicating if the player is drawing
dibujando = False
# Posición inicial del trazo actual | Start position of the current stroke
pos_inicio = None

# --- Funciones Espaciales | Spatial Functions ---
def limitar_punto(px, py):
    """Restringe una coordenada a los límites del área definida. | Restricts a coordinate to the defined area boundaries."""
    # Asegura que la coordenada x esté dentro del rango permitido | Ensures the x coordinate is within the allowed range
    x = max(LIMITE_MIN_X, min(px, LIMITE_MAX_X))
    # Asegura que la coordenada y esté dentro del rango permitido | Ensures the y coordinate is within the allowed range
    y = max(LIMITE_MIN_Y, min(py, LIMITE_MAX_Y))
    return (x, y)

def distancia_punto_linea(px, py, x1, y1, x2, y2):
    """Distancia de un punto a un segmento de línea. | Distance from a point to a line segment."""
    # Magnitud de la línea | Magnitude of the line
    mag_linea = math.hypot(x2 - x1, y2 - y1)
    if mag_linea == 0:
        # Si la línea es solo un punto, retorna distancia al punto | If the line is just a point, returns distance to the point
        return math.hypot(px - x1, py - y1)
    
    # Proyección del punto sobre la línea (normalizada) | Projection of the point onto the line (normalized)
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (mag_linea ** 2)
    
    # Verifica si la intersección más cercana está fuera de los extremos | Checks if the closest intersection is outside the endpoints
    if u < 0.0 or u > 1.0:
        ix, iy = (x1, y1) if u < 0.0 else (x2, y2)
        return math.hypot(px - ix, py - iy)
        
    # Intersección dentro del segmento | Intersection within the segment
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return math.hypot(px - ix, py - iy)

# --- Algoritmos de Conteo Divergente | Divergent Counting Algorithms ---
def obtener_conteos_divergentes(lineas_actuales):
    """Evalúa la visibilidad espacial interactiva de las líneas y círculos. | Evaluates the interactive spatial visibility of lines and circles."""
    
    # 1. Círculos Atravesados / Cubiertos | 1. Crossed / Covered Circles
    # Contador para círculos que interactúan con una línea | Counter for circles interacting with a line
    circulos_atravesados = 0
    for cx, cy in POSICIONES_CIRCULOS:
        
        # Validar si alguna línea atraviesa/toca el círculo | Validate if any line crosses/touches the circle
        esta_intersectado = False
        for linea in lineas_actuales:
            # Evalúa colisión tomando en cuenta el radio y grosor | Evaluates collision considering radius and thickness
            if distancia_punto_linea(cx, cy, linea['inicio'][0], linea['inicio'][1], linea['fin'][0], linea['fin'][1]) < (RADIO_CIRCULO + GROSOR_LINEA / 2):
                esta_intersectado = True
                break
        
        if esta_intersectado:
            circulos_atravesados += 1

    # 2. Líneas Visibles | 2. Visible Lines
    # Conteo de líneas que logran ser vistas por el usuario | Count of lines that can be seen by the user
    conteo_lineas_validas = 0
    for i, linea in enumerate(lineas_actuales):
        # El color naranja se omite en esta evaluación | Orange color is skipped in this evaluation
        if linea['color'] == NARANJA:
            continue 

        esta_visible = False
        x1, y1 = linea['inicio']
        x2, y2 = linea['fin']
        
        # Distancia para saber cuántas muestras tomar | Distance to know how many samples to take
        dist = math.hypot(x2 - x1, y2 - y1)
        num_muestras = max(2, int(dist / 5)) 

        # Escaneo de puntos sobre el segmento | Scanning points over the segment
        for j in range(num_muestras + 1):
            t = j / num_muestras if num_muestras > 0 else 0
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)

            punto_cubierto = False
            # Comparar contra las líneas dibujadas más tarde (capas superiores) | Compare against lines drawn later (upper layers)
            for linea_mas_nueva in lineas_actuales[i+1:]:
                if linea_mas_nueva['color'] != linea['color']:
                    if distancia_punto_linea(px, py, linea_mas_nueva['inicio'][0], linea_mas_nueva['inicio'][1], linea_mas_nueva['fin'][0], linea_mas_nueva['fin'][1]) <= GROSOR_LINEA / 2:
                        punto_cubierto = True
                        break
                        
            # Si un punto de muestreo sobrevive la oclusión, la línea es visible | If a sampling point survives occlusion, the line is visible
            if not punto_cubierto:
                esta_visible = True
                break

        if esta_visible:
            conteo_lineas_validas += 1

    # Calcula cuántos diamantes dibujar como indicador | Calculates how many diamonds to draw as indicator
    indicador_lineas = max(0, 4 - conteo_lineas_validas)
    return indicador_lineas, circulos_atravesados

# --- Funciones de Dibujo UI | UI Drawing Functions ---
def dibujar_simbolo_diamante(superficie, x, y, tamano=12):
    """Dibuja un diamante en cuatro cuadrantes de color. | Draws a diamond in four color quadrants."""
    centro = (x, y)
    arriba = (x, y - tamano)
    abajo = (x, y + tamano)
    izquierda = (x - tamano, y)
    derecha = (x + tamano, y)
    
    # Dibujo de triángulos que forman el diamante | Drawing of triangles forming the diamond
    pygame.draw.polygon(superficie, NEGRO, [centro, arriba, derecha])
    pygame.draw.polygon(superficie, AZUL, [centro, derecha, abajo])
    pygame.draw.polygon(superficie, NEGRO, [centro, abajo, izquierda])
    pygame.draw.polygon(superficie, AZUL, [centro, izquierda, arriba])
    
    # Líneas divisorias en color naranja | Dividing lines in orange
    pygame.draw.line(superficie, NARANJA, arriba, abajo, 2)
    pygame.draw.line(superficie, NARANJA, izquierda, derecha, 2)

def dibujar_interfaz(ind_lineas, ind_colores, ind_circulos):
    """Dibuja los indicadores interactivos. | Draws the interactive indicators."""
    # Indicadores alineados a x=70 | Indicators aligned to x=70
    
    # 1. Indicador de Líneas | 1. Lines Indicator
    pygame.draw.line(pantalla, NEGRO, (15, 20), (35, 20), 4)
    for i in range(ind_lineas):
        dibujar_simbolo_diamante(pantalla, 70 + (i * 30), 20)
        
    # 2. Indicador de Colores (Negro, Azul, y Naranja con borde negro) | 2. Colors Indicator (Black, Blue, and Orange with black border)
    pygame.draw.circle(pantalla, NEGRO, (20, 50), 4)
    pygame.draw.circle(pantalla, AZUL, (32, 50), 4)
    pygame.draw.circle(pantalla, NEGRO, (44, 50), 5)  
    pygame.draw.circle(pantalla, NARANJA, (44, 50), 4) 
    for i in range(ind_colores):
        dibujar_simbolo_diamante(pantalla, 70 + (i * 30), 50)
        
    # 3. Indicador de Círculos | 3. Circles Indicator
    pygame.draw.circle(pantalla, AZUL, (25, 80), 8, 2)
    for i in range(ind_circulos):
        dibujar_simbolo_diamante(pantalla, 70 + (i * 30), 80)

    # Paleta de Selección Superior Derecha | Top Right Selection Palette
    pygame.draw.rect(pantalla, NEGRO, (650, 20, 40, 40))
    pygame.draw.rect(pantalla, NARANJA, (700, 20, 40, 40))
    pygame.draw.rect(pantalla, AZUL, (750, 20, 40, 40))
    
    # Selección visual de color (recuadro) | Visual color selection (box)
    if color_actual == NEGRO:
        pygame.draw.rect(pantalla, AZUL, (648, 18, 44, 44), 3)
    elif color_actual == NARANJA:
        pygame.draw.rect(pantalla, NEGRO, (698, 18, 44, 44), 3)
    elif color_actual == AZUL:
        pygame.draw.rect(pantalla, NEGRO, (748, 18, 44, 44), 3)

# --- Bucle Principal | Main Loop ---
# Control de cuadros por segundo | Frames per second control
reloj = pygame.time.Clock()
# Variable para mantener corriendo el bucle | Variable to keep the loop running
ejecutando = True

while ejecutando:
    # Obtener posición del mouse de Pygame | Get mouse position from Pygame
    pos_raton_cruda = pygame.mouse.get_pos()
    
    # Evaluar lista de líneas activas y previas en tiempo real | Evaluate active and previous lines in real time
    lineas_activas = list(lineas)
    if dibujando:
        # Límite espacial donde el mouse está operando | Spatial limit where the mouse is operating
        raton_limitado = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1])
        if pos_inicio != raton_limitado:
            # Añadir línea dinámica mientras se mantiene pulsado | Add dynamic line while holding click
            lineas_activas.append({'inicio': pos_inicio, 'fin': raton_limitado, 'color': color_actual})

    # Generación de indicadores según la actividad actual | Generation of indicators based on current activity
    indicador_lineas, circulos_atravesados = obtener_conteos_divergentes(lineas_activas)
    
    # Gestión de eventos del usuario | User event management
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_q: 
                ejecutando = False
            elif evento.key == pygame.K_r: 
                # Vaciar lista de líneas para reiniciar | Empty lines list to reset
                lineas.clear()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: 
                # Detección de selección en paleta de colores | Color palette selection detection
                if 20 <= pos_raton_cruda[1] <= 60 and 650 <= pos_raton_cruda[0] <= 790:
                    if 650 <= pos_raton_cruda[0] <= 690: color_actual = NEGRO
                    elif 700 <= pos_raton_cruda[0] <= 740: color_actual = NARANJA
                    elif 750 <= pos_raton_cruda[0] <= 790: color_actual = AZUL
                else:
                    # Inicia el trazado en el plano | Starts stroke on the plane
                    dibujando = True
                    pos_inicio = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1])
            elif evento.button == 3: 
                # Lógica del borrador | Eraser logic
                lineas_a_eliminar = []
                for linea in lineas:
                    if distancia_punto_linea(pos_raton_cruda[0], pos_raton_cruda[1], linea['inicio'][0], linea['inicio'][1], linea['fin'][0], linea['fin'][1]) <= GROSOR_LINEA / 2:
                        lineas_a_eliminar.append(linea)
                        break 
                for linea in lineas_a_eliminar: lineas.remove(linea)
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1 and dibujando:
                dibujando = False
                pos_fin = limitar_punto(pos_raton_cruda[0], pos_raton_cruda[1])
                # Guardar trazo final si es válido | Save final stroke if valid
                if pos_inicio != pos_fin:
                    lineas.append({'inicio': pos_inicio, 'fin': pos_fin, 'color': color_actual})

    # 1. Renderizado del Lienzo | 1. Canvas Rendering
    pantalla.fill(NARANJA) 
    for pos in POSICIONES_CIRCULOS:
        pygame.draw.circle(pantalla, AZUL, pos, RADIO_CIRCULO)
    for linea in lineas_activas:
        pygame.draw.line(pantalla, linea['color'], linea['inicio'], linea['fin'], GROSOR_LINEA)
        # Redondeo en los vértices del trazado | Rounding at the vertices of the stroke
        pygame.draw.circle(pantalla, linea['color'], linea['inicio'], GROSOR_LINEA // 2)
        pygame.draw.circle(pantalla, linea['color'], linea['fin'], GROSOR_LINEA // 2)

    # 2. Análisis Dinámico de Pixeles para la Colorimetría | 2. Dynamic Pixel Analysis for Colorimetry
    # Genera un rectángulo de colisión | Generates a collision rectangle
    rectangulo = pygame.Rect(LIMITE_MIN_X, LIMITE_MIN_Y, LIMITE_MAX_X - LIMITE_MIN_X, LIMITE_MAX_Y - LIMITE_MIN_Y)
    # Extrae el área para ser analizada | Extracts the area to be analyzed
    subsuperficie = pantalla.subsurface(rectangulo)
    # Escala la imagen del área restringida | Scales the restricted area image
    sub_pequena = pygame.transform.scale(subsuperficie, (80, 60)) 
    # Convierte a matriz para inspección rápida | Converts to array for fast inspection
    matriz_pixeles = pygame.PixelArray(sub_pequena)
    
    colores_en_area = set()
    for x in range(80):
        for y in range(60):
            # Obtiene los valores RGB por pixel | Gets RGB values per pixel
            r, g, b, a = sub_pequena.unmap_rgb(matriz_pixeles[x,y])
            if (r, g, b) == NEGRO: colores_en_area.add('black')
            elif (r, g, b) == NARANJA: colores_en_area.add('orange')
            elif (r, g, b) == AZUL: colores_en_area.add('blue')
    matriz_pixeles.close()
    
    # 3 - La cantidad de colores únicos presentes | 3 - The amount of unique colors present
    indicador_color = max(0, 3 - len(colores_en_area))
    
    # Bonus: Si el único color que quedó es el Naranja, se gana un rombo extra | Bonus: If the only remaining color is Orange, an extra diamond is earned
    if colores_en_area == {'orange'}:
        indicador_color += 1

    # 3. Dibujo de UI | 3. UI Drawing 
    dibujar_interfaz(indicador_lineas, indicador_color, circulos_atravesados)

    # Refresca la ventana de Pygame | Refreshes the Pygame window
    pygame.display.flip()
    # Bloquea los FPS a un máximo de 60 | Locks FPS to a maximum of 60
    reloj.tick(60)

# Cierre seguro del programa | Safe shutdown of the program
pygame.quit()
sys.exit()