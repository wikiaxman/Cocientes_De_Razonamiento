# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 12:06:54 2026

@author: AXMAN (Modificado v2)
"""

import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana (1080x720p)
WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Daltonismo - Paleta Okabe-Ito")

# Colores de la paleta Okabe-Ito (Nombre ES, Nombre EN, RGB)
okabe_ito_palette = [
    ("Naranja", "Orange", (230, 159, 0)),
    ("Azul Cielo", "Sky Blue", (86, 180, 233)),
    ("Verde Azulado", "Bluish Green", (0, 158, 115)),
    ("Amarillo", "Yellow", (240, 228, 66)),
    ("Azul", "Blue", (0, 114, 178)),
    ("Bermellón", "Vermillion", (213, 94, 0)),
    ("Rosa", "Pink", (204, 121, 167)),
    ("Negro", "Black", (0, 0, 0)) 
]

# Configuración de fuentes
font = pygame.font.SysFont("Arial", 26, bold=True)
btn_font = pygame.font.SysFont("Arial", 18, bold=True)

# Control de frames por segundo (FPS)
clock = pygame.time.Clock()

# Estado de simulación actual
current_mode = "Normal"

# Configuración de los 4 botones inferiores con etiquetas bilingües
# Se subió la posición Y a 625 para dar espacio al texto secundario
button_radius = 20
buttons = [
    {"mode": "Normal", "pos": (216, 625), "label_es": "Normal", "label_en": "Normal Vision"},
    {"mode": "Protanopia", "pos": (432, 625), "label_es": "Protanopia (Rojo)", "label_en": "Protanopia (Red)"},
    {"mode": "Deuteranopia", "pos": (648, 625), "label_es": "Deuteranopia (Verde)", "label_en": "Deuteranopy (Green)"},
    {"mode": "Tritanopia", "pos": (864, 625), "label_es": "Tritanopia (Azul)", "label_en": "Tritanopy (Blue)"}
]

def simulate_colorblindness(rgb, mode):
    """Aplica matrices de transformación simplificadas para simular daltonismo."""
    if mode == "Normal":
        return rgb
    
    r, g, b = rgb
    if mode == "Protanopia":  # Ceguera al rojo
        nr = int(0.567 * r + 0.433 * g + 0.0 * b)
        ng = int(0.558 * r + 0.442 * g + 0.0 * b)
        nb = int(0.0 * r + 0.242 * g + 0.758 * b)
    elif mode == "Deuteranopia":  # Ceguera al verde
        nr = int(0.625 * r + 0.375 * g + 0.0 * b)
        ng = int(0.70 * r + 0.30 * g + 0.0 * b)
        nb = int(0.0 * r + 0.30 * g + 0.70 * b)
    elif mode == "Tritanopia":  # Ceguera al azul
        nr = int(0.95 * r + 0.05 * g + 0.0 * b)
        ng = int(0.0 * r + 0.433 * g + 0.567 * b)
        nb = int(0.0 * r + 0.475 * g + 0.525 * b)
    else:
        return rgb

    return (max(0, min(255, nr)), max(0, min(255, ng)), max(0, min(255, nb)))

# Bucle principal del juego
running = True
while running:
    # Manejo de eventos
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]:
            running = False
        
        # Detectar clics en los botones
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for btn in buttons:
                bx, by = btn["pos"]
                distance = ((mouse_x - bx) ** 2 + (mouse_y - by) ** 2) ** 0.5
                if distance <= button_radius:
                    current_mode = btn["mode"]

    # Fondo completamente negro
    screen.fill((0, 0, 0))

    # ---- SECCIÓN 1: RENDERIZADO DE LA PALETA ----
    start_y = 45
    spacing_y = 68
    circle_x = WIDTH // 2
    radius = 20

    for i, (name_es, name_en, original_color) in enumerate(okabe_ito_palette):
        current_y = start_y + i * spacing_y
        
        simulated_color = simulate_colorblindness(original_color, current_mode)

        text_es = font.render(name_es, True, simulated_color)
        text_en = font.render(name_en, True, simulated_color)
        
        rect_es = text_es.get_rect(midleft=(circle_x + 40, current_y))
        rect_en = text_en.get_rect(midright=(circle_x - 40, current_y))

        if name_es == "Negro":
            pygame.draw.circle(screen, simulated_color, (circle_x, current_y), radius)
            pygame.draw.circle(screen, (255, 255, 255), (circle_x, current_y), radius, 2)
            pygame.draw.rect(screen, (255, 255, 255), rect_es.inflate(15, 8), border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), rect_en.inflate(15, 8), border_radius=5)
        else:
            pygame.draw.circle(screen, simulated_color, (circle_x, current_y), radius)

        screen.blit(text_es, rect_es)
        screen.blit(text_en, rect_en)

    # ---- SECCIÓN 2: RENDERIZADO DE BOTONES DE CONTROL ----
    # Línea divisoria discreta
    pygame.draw.line(screen, (50, 50, 50), (50, 575), (WIDTH - 50, 575), 2)

    for btn in buttons:
        bx, by = btn["pos"]
        is_active = (current_mode == btn["mode"])
        
        base_color = (255, 255, 255) if is_active else (100, 100, 100)
        
        # Dibujar el botón
        pygame.draw.circle(screen, base_color, (bx, by), button_radius, 2)
        if is_active:
            pygame.draw.circle(screen, (255, 255, 255), (bx, by), button_radius - 6)
        
        # 1. Renderizar la etiqueta en Español (Línea superior)
        text_es = btn_font.render(btn["label_es"], True, base_color)
        rect_es = text_es.get_rect(center=(bx, by + 32))
        screen.blit(text_es, rect_es)
        
        # 2. Renderizar la etiqueta en Inglés (Línea inferior)
        text_en = btn_font.render(btn["label_en"], True, base_color)
        rect_en = text_en.get_rect(center=(bx, by + 54))
        screen.blit(text_en, rect_en)

    # Actualizar la pantalla
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()