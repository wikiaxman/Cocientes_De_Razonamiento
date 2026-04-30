# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 18:44:02 2026 | Creado en Viernes 24 de Abril de 2026
a las 18:44:02 horas

@author: AXMAN, Gemini y Claude
"""

# Importar librerías estándar y de terceros | Import standard and third-party libraries
import pygame
import math
import sys
import numpy as np

# Intentar importar el compilador JIT de Numba para optimización | Try importing Numba JIT compiler for optimization
try:
    from numba import njit
except ImportError:
    # Si Numba no está instalado, crear un decorador simulado | If Numba is not installed, create a dummy decorator
    def njit(**kw):
        def deco(f): return f
        return deco

# ── Constantes y Configuración | Constants and Configuration ────────────────────────────────────────────────────────────────
# Dimensiones de la ventana principal | Main window dimensions
ANCHO, ALTO  = 800, 800 # WIDTH, HEIGHT
# Atributos de dibujo | Drawing attributes
GROSOR_LINEA = 40 # LINE_THICKNESS
RADIO_CIRCULO  = 40 # CIRCLE_RADIUS

# Límites del área interactiva | Interactive area boundaries
LIMITE_MIN_X, LIMITE_MAX_X = 80,  720 # BOUND_MIN_X, BOUND_MAX_X
LIMITE_MIN_Y, LIMITE_MAX_Y = 160, 640 # BOUND_MIN_Y, BOUND_MAX_Y
# Cálculo del ancho y alto del área de dibujo | Calculation of drawing area width and height
AREA_ANCHO = LIMITE_MAX_X - LIMITE_MIN_X   # 640 | AREA_W
AREA_ALTO = LIMITE_MAX_Y - LIMITE_MIN_Y   # 480 | AREA_H

# Definición de paleta de colores RGB permitidos | Definition of allowed RGB color palette
NEGRO  = (0,   0,   0  ) # BLACK
NARANJA = (230, 159, 0  ) # ORANGE
AZUL   = (0,   114, 178) # BLUE

# Color de fondo para superficie auxiliar de líneas | Background color for auxiliary line surface
# Gris medio que NO coincide con el juego para evitar confusiones al comparar | Medium gray that DOES NOT match the game to avoid confusion when comparing
FONDO_NEUTRAL = (128, 128, 128) # NEUTRAL_BG

# Coordenadas estáticas de los círculos base | Static coordinates of the base circles
POSICIONES_CIRCULOS = [[260, 360], [520, 360], [200, 520], [600, 520]] # CIRCLE_POSITIONS

# ─────────────────────────────────────────────────────────────────────────────
# Numba JIT 1: detección de colores en el área | Numba JIT 1: area color detection
# ─────────────────────────────────────────────────────────────────────────────
@njit(cache=False)
def _detectar_colores(pixeles): # _detect_colors
    """
    Recorre cada píxel del array. Devuelve presencia de los 3 colores. | Iterates each array pixel. Returns presence of the 3 colors.
    Salida anticipada (early-exit) cuando los 3 ya están. | Early-exit when all 3 are found.
    """
    # Inicialización de banderas de color | Color flags initialization
    tiene_negro = False; tiene_naranja = False; tiene_azul = False # has_black, has_orange, has_blue
    
    # Bucle anidado para inspeccionar coordenadas X e Y | Nested loop to inspect X and Y coordinates
    for x in range(pixeles.shape[0]):
        for y in range(pixeles.shape[1]):
            # Extracción de canales R, G, B | R, G, B channel extraction
            r = pixeles[x, y, 0]; g = pixeles[x, y, 1]; b = pixeles[x, y, 2]
            
            # Verificación contra paleta exacta | Verification against exact palette
            if   r == 0   and g == 0   and b == 0:   tiene_negro  = True
            elif r == 230 and g == 159 and b == 0:   tiene_naranja = True
            elif r == 0   and g == 114 and b == 178: tiene_azul   = True
            
            # Condición de salida rápida si todos están presentes | Fast exit condition if all are present
            if tiene_negro and tiene_naranja and tiene_azul:
                return True, True, True
                
    return tiene_negro, tiene_naranja, tiene_azul

# ─────────────────────────────────────────────────────────────────────────────
# Numba JIT 2: ¿alguna línea coincide en la pantalla final? | Numba JIT 2: does any line match the final screen?
# ─────────────────────────────────────────────────────────────────────────────
@njit(cache=False)
def _algun_pixel_coincide(solo_linea, area_pantalla, r, g, b): # _any_pixel_match
    """
    Retorna True si al menos un píxel de la línea sobrevive a la oclusión. | Returns True if at least one pixel of the line survives occlusion.
    """
    # Dimensiones de las matrices a comparar | Dimensions of matrices to compare
    W = solo_linea.shape[0]; H = solo_linea.shape[1]
    
    for x in range(W):
        for y in range(H):
            # 1. Verifica si este píxel pertenecía a la línea aislada | 1. Check if this pixel belonged to the isolated line
            if (solo_linea[x, y, 0] == r and
                solo_linea[x, y, 1] == g and
                solo_linea[x, y, 2] == b):
                # 2. Verifica si el mismo píxel exacto sobrevivió en el lienzo final | 2. Check if the exact same pixel survived on the final canvas
                if (area_pantalla[x, y, 0] == r and
                    area_pantalla[x, y, 1] == g and
                    area_pantalla[x, y, 2] == b):
                    return True # ¡La línea es visible! | The line is visible!
    return False

# ── Calentar JIT antes del game loop | Warm up JIT before game loop ─────────────────────────────────────────
# Matriz ficticia para obligar a Numba a precompilar | Dummy array to force Numba to precompile
_ficticio = np.zeros((1, 1, 3), dtype=np.uint8) # _dummy
_detectar_colores(_ficticio)
_algun_pixel_coincide(_ficticio, _ficticio, 0, 0, 0)

# ── Inicializar Pygame | Initialize Pygame ────────────────────────────────────────────────────────
pygame.init()
# Crear ventana principal | Create main window
pantalla = pygame.display.set_mode((ANCHO, ALTO)) # screen
pygame.display.set_caption("Task 1 - Divergent Puzzle")

# Superficies auxiliares en memoria para análisis matemático | In-memory auxiliary surfaces for math analysis
# _superficie_escena : copia del área real de la pantalla | copy of real screen area
# _superficie_linea  : una línea sola para aislamiento | single line for isolation
_superficie_escena = pygame.Surface((AREA_ANCHO, AREA_ALTO)) # _scene_surf
_superficie_linea  = pygame.Surface((AREA_ANCHO, AREA_ALTO)) # _line_surf

# Variables de Estado del Juego | Game State Variables
lineas        = [] # lines
color_actual = NEGRO # current_color
dibujando      = False # drawing
pos_inicio    = None # start_pos


# ── Helpers geométricos | Geometric helpers ───────────────────────────────────────────────────────
def limitar_punto(px, py): # clamp_point
    # Forzar coordenadas X e Y dentro de la caja de dibujo | Force X and Y coordinates inside drawing box
    return (max(LIMITE_MIN_X, min(px, LIMITE_MAX_X)),
            max(LIMITE_MIN_Y, min(py, LIMITE_MAX_Y)))

def distancia_punto_linea(px, py, x1, y1, x2, y2): # point_line_distance
    # Magnitud (longitud) de la línea | Magnitude (length) of line
    magnitud_linea = math.hypot(x2-x1, y2-y1) # lm
    if magnitud_linea == 0:
        return math.hypot(px-x1, py-y1)
    
    # Ecuación de proyección escalar | Scalar projection equation
    u = ((px-x1)*(x2-x1) + (py-y1)*(y2-y1)) / (magnitud_linea**2)
    # Limitar el escalar al rango exacto de la línea [0, 1] | Limit scalar to exact line range [0, 1]
    u = max(0.0, min(1.0, u))
    
    # Retornar hipotenusa desde el punto hasta la proyección ortogonal | Return hypotenuse from point to orthogonal projection
    return math.hypot(px-(x1+u*(x2-x1)), py-(y1+u*(y2-y1)))


# ── Pipeline pixel-perfect post-render ───────────────────────────────────────
def analizar_escena(lineas_activas): # analyze_scene
    """
    Ejecuta el análisis de visibilidad y colorimetría extrayendo píxeles de Pygame. | Executes visibility and colorimetry analysis extracting Pygame pixels.
    """
    # ─ A) Píxeles reales del área confinada | A) Real pixels of confined area ─
    # Volcar recorte visual actual en memoria | Dump current visual crop into memory
    _superficie_escena.blit(
        pantalla, (0, 0),
        pygame.Rect(LIMITE_MIN_X, LIMITE_MIN_Y, AREA_ANCHO, AREA_ALTO)
    )
    # Convertir a matriz 3D RGB | Convert to 3D RGB array
    pixeles_escena = pygame.surfarray.array3d(_superficie_escena) # scene_pixels

    # ─ B) Indicador de colores | B) Color indicator ─
    # Llamar subrutina JIT | Call JIT subroutine
    tiene_negro, tiene_naranja, tiene_azul = _detectar_colores(pixeles_escena)
    
    # Agrupar colores encontrados en un conjunto de Python | Group found colors into a Python set
    encontrados = set() # found
    if tiene_negro:  encontrados.add('negro')
    if tiene_naranja: encontrados.add('naranja')
    if tiene_azul:   encontrados.add('azul')
    
    # Calcular cantidad de diamantes faltantes | Calculate missing diamonds amount
    indicador_color = max(0, 3 - len(encontrados)) # color_indicator
    if encontrados == {'naranja'}:
        indicador_color += 1   # bonus: solo queda naranja | bonus: only orange left

    # ─ C) Indicador de líneas (pixel-perfect) | C) Line indicator (pixel-perfect) ─
    conteo_lineas_validas = 0 # valid_lines_count
    for linea in lineas_activas:
        if linea['color'] == NARANJA:
            continue                              # Naranjas nunca cuentan | Oranges never count

        # Render aislado de esta línea con limpieza neutra | Isolated render of this line with neutral wipe
        _superficie_linea.fill(FONDO_NEUTRAL)
        # Adaptar coordenadas globales a coordenadas locales de la sub-superficie | Adapt global coordinates to local subsurface coordinates
        inicio_local = (linea['inicio'][0] - LIMITE_MIN_X, linea['inicio'][1] - LIMITE_MIN_Y) # s
        fin_local = (linea['fin'][0]   - LIMITE_MIN_X, linea['fin'][1]   - LIMITE_MIN_Y) # e
        
        # Trazar línea en aislamiento | Draw line in isolation
        pygame.draw.line(_superficie_linea,   linea['color'], inicio_local, fin_local, GROSOR_LINEA)
        pygame.draw.circle(_superficie_linea, linea['color'], inicio_local, GROSOR_LINEA // 2)
        pygame.draw.circle(_superficie_linea, linea['color'], fin_local, GROSOR_LINEA // 2)

        # Convertir a arreglo 3D para matemáticas | Convert to 3D array for math
        pixeles_linea = pygame.surfarray.array3d(_superficie_linea) # line_pixels
        r, g, b = linea['color']
        
        # Validar superposición de píxeles | Validate pixel overlapping
        if _algun_pixel_coincide(pixeles_linea, pixeles_escena, r, g, b):
            conteo_lineas_validas += 1

    # Calcular diamantes de líneas restando válidas al total requerido (4) | Calculate line diamonds subtracting valid from required total (4)
    indicador_lineas = max(0, 4 - conteo_lineas_validas) # lines_indicator

    # ─ D) Círculos atravesados (geometría) | D) Crossed circles (geometry) ─
    circulos_atravesados = 0 # crossed_circles
    for cx, cy in POSICIONES_CIRCULOS:
        for linea in lineas_activas:
            # Medir proximidad matemática entre centro y segmento | Measure mathematical proximity between center and segment
            if distancia_punto_linea(cx, cy,
                                   linea['inicio'][0], linea['inicio'][1],
                                   linea['fin'][0],   linea['fin'][1]) \
               < (RADIO_CIRCULO + GROSOR_LINEA / 2):
                circulos_atravesados += 1
                break

    return indicador_lineas, indicador_color, circulos_atravesados


# ── Interfaz de Usuario UI | User Interface ────────────────────────────────────────────────────────────────────────
def dibujar_diamante(superficie, x, y, tamano=12): # draw_diamond
    """Dibuja polígono geométrico de estado. | Draws geometric status polygon."""
    # Vértices calculados (centro, arriba, abajo, izq, der) | Calculated vertices (center, top, bottom, left, right)
    c = (x,y); arr = (x,y-tamano); ab = (x,y+tamano); izq = (x-tamano,y); der = (x+tamano,y) # c, t, b, l, r
    
    # Pintado de cuartos triangulares | Painting of triangular quarters
    pygame.draw.polygon(superficie, NEGRO,  [c, arr, der])
    pygame.draw.polygon(superficie, AZUL,   [c, der, ab])
    pygame.draw.polygon(superficie, NEGRO,  [c, ab, izq])
    pygame.draw.polygon(superficie, AZUL,   [c, izq, arr])
    
    # Líneas cruzadas de detalle | Cross lines detailing
    pygame.draw.line(superficie, NARANJA, arr, ab, 2)
    pygame.draw.line(superficie, NARANJA, izq, der, 2)


def dibujar_interfaz(ind_lineas, ind_colores, ind_circulos): # draw_ui
    """Renderiza cabecera interactiva. | Renders interactive header."""
    # Fila 1: líneas | Row 1: lines
    pygame.draw.line(pantalla, NEGRO, (15,20), (35,20), 4)
    for i in range(ind_lineas):   dibujar_diamante(pantalla, 70+i*30, 20)

    # Fila 2: colores | Row 2: colors
    pygame.draw.circle(pantalla, NEGRO,  (20,50), 4)
    pygame.draw.circle(pantalla, AZUL,   (32,50), 4)
    pygame.draw.circle(pantalla, NEGRO,  (44,50), 5)
    pygame.draw.circle(pantalla, NARANJA, (44,50), 4)
    for i in range(ind_colores):  dibujar_diamante(pantalla, 70+i*30, 50)

    # Fila 3: círculos | Row 3: circles
    pygame.draw.circle(pantalla, AZUL, (25,80), 8, 2)
    for i in range(ind_circulos): dibujar_diamante(pantalla, 70+i*30, 80)

    # Paleta interactiva | Interactive palette
    pygame.draw.rect(pantalla, NEGRO,  (650,20,40,40))
    pygame.draw.rect(pantalla, NARANJA, (700,20,40,40))
    pygame.draw.rect(pantalla, AZUL,   (750,20,40,40))
    
    # Localizaciones visuales para borde de selección | Visual locations for selection border
    desplazamientos = {NEGRO:(648,18), NARANJA:(698,18), AZUL:(748,18)} # offsets
    des_x, des_y = desplazamientos[color_actual] # ox, oy
    borde = AZUL if color_actual == NEGRO else NEGRO # border
    pygame.draw.rect(pantalla, borde, (des_x,des_y,44,44), 3)


# ── Loop principal de ejecución | Main execution loop ────────────────────────────────────────────────────────────
# Objeto para controlar framerate | Object to control framerate
reloj   = pygame.time.Clock() # clock
# Control de ciclo infinito | Infinite loop control
ejecutando = True # running

while ejecutando:
    # Rastreo crudo del hardware del mouse | Raw mouse hardware tracking
    raton_crudo = pygame.mouse.get_pos() # raw_mouse

    # Construir lista de líneas activas (commits guardados + preview dinámica en curso) | Build active lines list (saved commits + dynamic preview ongoing)
    lineas_activas = list(lineas) # active_lines
    if dibujando:
        # Delimitar arrastre actual | Clamp current drag
        raton_lim = limitar_punto(raton_crudo[0], raton_crudo[1]) # cm
        if pos_inicio != raton_lim:
            lineas_activas.append({'inicio': pos_inicio, 'fin': raton_lim, 'color': color_actual})

    # Procesador de eventos de teclado/mouse | Keyboard/mouse event processor
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if   evento.key == pygame.K_q: ejecutando = False
            # Tecla R borra todo el lienzo de memoria | Key R clears entire memory canvas
            elif evento.key == pygame.K_r: lineas.clear()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                # Comprobar clicks en área de paleta de interfaz | Check clicks on interface palette area
                if 20 <= raton_crudo[1] <= 60 and 650 <= raton_crudo[0] <= 790:
                    if   raton_crudo[0] <= 690: color_actual = NEGRO
                    elif raton_crudo[0] <= 740: color_actual = NARANJA
                    else:                     color_actual = AZUL
                else:
                    # Iniciar nueva línea topológica | Start new topological line
                    dibujando   = True
                    pos_inicio = limitar_punto(raton_crudo[0], raton_crudo[1])
            elif evento.button == 3:
                # Botón derecho actúa como borrador matemático local | Right button acts as local mathematical eraser
                for linea in lineas:
                    if distancia_punto_linea(raton_crudo[0], raton_crudo[1],
                                           linea['inicio'][0], linea['inicio'][1],
                                           linea['fin'][0],   linea['fin'][1]) \
                       <= GROSOR_LINEA / 2:
                        lineas.remove(linea); break
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1 and dibujando:
                dibujando = False
                pos_fin = limitar_punto(raton_crudo[0], raton_crudo[1]) # ep
                # Commit final de trazo a lista permanente | Final stroke commit to permanent list
                if pos_inicio != pos_fin:
                    lineas.append({'inicio': pos_inicio, 'fin': pos_fin, 'color': color_actual})

    # ── 1. Render del lienzo de trabajo | 1. Working canvas render ──────────────────────────────────────────────────
    # Capa fondo | Background layer
    pantalla.fill(NARANJA)
    # Capa círculos obstructivos | Obstructive circles layer
    for pos in POSICIONES_CIRCULOS:
        pygame.draw.circle(pantalla, AZUL, pos, RADIO_CIRCULO)
    # Capa trazos del jugador dinámicos e históricos | Historical and dynamic player strokes layer
    for linea in lineas_activas:
        pygame.draw.line(pantalla,   linea['color'], linea['inicio'], linea['fin'], GROSOR_LINEA)
        pygame.draw.circle(pantalla, linea['color'], linea['inicio'], GROSOR_LINEA // 2)
        pygame.draw.circle(pantalla, linea['color'], linea['fin'],   GROSOR_LINEA // 2)

    # ── 2. Análisis pixel-perfect (post-render, pre-UI) | 2. Pixel-perfect analysis ──────────────────────
    # Llamada al motor de procesamiento analítico | Call to analytical processing engine
    ind_lineas, ind_color, ind_circulos = analizar_escena(lineas_activas)

    # ── 3. Superposición de Interfaz (UI) | 3. User Interface Overlay ─────────────────────────────────────────────────────────────────
    # Dibujar métricas procesadas encima del lienzo base | Draw processed metrics on top of base canvas
    dibujar_interfaz(ind_lineas, ind_color, ind_circulos)

    # Actualizar hardware de pantalla visual | Update visual screen hardware
    pygame.display.flip()
    # Limitar ciclos de CPU a 60 FPS fijos | Cap CPU cycles to fixed 60 FPS
    reloj.tick(60)

# Cierre ordenado de módulo y terminal en escape | Clean exit of module and terminal on escape
pygame.quit()
sys.exit()