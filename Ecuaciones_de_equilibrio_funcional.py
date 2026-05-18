# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 21:28:06 2026 | Creado en Martes 21 de Abril de 2026
a las 21:28:06 horas

@author: AXMAN y Gemini
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from numba import njit, prange

# --- Configuración | Configuration ---
poblacion = 100_000 # population
tareas_totales = 20 # total_tasks
espacio_criterio = 4 # criteria_space: Representado como 'C' en las fórmulas | Represented as 'C' in the formulas

@njit
def calcular_puntuacion_final(media_calidad, completadas, total): # calculate_final_score (Raíces cuadradas / Square roots)
    """
    Aplica la fórmula de puntuación final original: | Applies the original final scoring formula: 
    g = Cr * sqrt(Cr) * sqrt(n * (100 / N))
    """
    factor_completitud = np.sqrt((completadas * 100.0) / total) # completion_factor
    return media_calidad * np.sqrt(media_calidad) * factor_completitud

@njit
def calcular_puntuacion_logaritmica(media_calidad, completadas): # calculate_logarithmic_score
    """
    Aplica la fórmula de puntuación logarítmica: | Applies the logarithmic scoring formula:
    f = Cr * sqrt(n) * log10(n + 1)
    """
    return media_calidad * np.sqrt(completadas) * np.log10(completadas + 1.0)

# --- Simulación Acelerada con Numba | Accelerated Simulation with Numba ---
@njit(parallel=True, nogil=True)
def simular_poblacion(pob, tareas_tot, esp_crit):
    """
    Simula las puntuaciones usando Numba para compilar el código a C y paralelizar el bucle.
    Simulates scores using Numba to compile the code to C and parallelize the loop.
    """
    punt_finales_lineales = np.empty(pob, dtype=np.float64) # linear_final_scores
    punt_finales_sigmoides = np.empty(pob, dtype=np.float64) # sigmoid_final_scores
    punt_log_lineales = np.empty(pob, dtype=np.float64) # linear_log_scores
    punt_log_sigmoides = np.empty(pob, dtype=np.float64) # sigmoid_log_scores

    for persona in prange(pob): 
        tiradas = np.random.randint(-esp_crit, esp_crit + 1, tareas_tot) # rolls
        
        # 1. Cálculo de Calidad Lineal | 1. Linear Quality Calculation
        calidades_l = ((tiradas + esp_crit) / (2.0 * esp_crit)) * 100.0 # l_qualities
        media_l = np.mean(calidades_l) # l_mean
        
        # 2. Cálculo de Calidad Sigmoide | 2. Sigmoid Quality Calculation
        calidades_s = 100.0 / (1.0 + 10.0**(-tiradas / esp_crit)) # s_qualities
        media_s = np.mean(calidades_s) # s_mean
        
        completadas = np.random.randint(tareas_tot, tareas_tot + 1) # completed
        
        # Aplicar ecuaciones | Apply equations
        punt_finales_lineales[persona] = calcular_puntuacion_final(media_l, completadas, tareas_tot)
        punt_finales_sigmoides[persona] = calcular_puntuacion_final(media_s, completadas, tareas_tot)
        punt_log_lineales[persona] = calcular_puntuacion_logaritmica(media_l, completadas)
        punt_log_sigmoides[persona] = calcular_puntuacion_logaritmica(media_s, completadas)

    return punt_finales_lineales, punt_finales_sigmoides, punt_log_lineales, punt_log_sigmoides

# Tiempo de inicio de la simulacíon | Initial time of the simulation
inicio = time.perf_counter_ns()

# Ejecución de la simulación | Execution of the simulation
p_lineal_raiz, p_sigmoide_raiz, p_lineal_log, p_sigmoide_log = simular_poblacion(poblacion, tareas_totales, espacio_criterio)

# Tiempo de finalización de la simulación | Finishing time of the simulation 
fin = time.perf_counter_ns()

# Duracion de la simulación | Simulation duration
duración = (fin - inicio)/1_000_000_000
print(f"Tomó {duración} segundos en completarse la simulación")
print(f"It took {duración} seconds to complete the simulation")

# Estilo global para las gráficas | Global style for plots
plt.style.use('seaborn-v0_8-whitegrid')

# Strings de ecuaciones en LaTeX | Equation strings in LaTeX
eq_raiz = r"$g(\mu_{C_r}, n) = \mu_{C_r} \cdot \sqrt{\mu_{C_r}} \cdot \sqrt{n \cdot (\frac{100}{N})}$"
eq_log = r"$f(\mu_{C_r}, n) = \mu_{C_r} \cdot \sqrt{n} \cdot \log_{10}(n+1)$"
eq_calidad_lineal = r"Modelo Lineal | Linear Model: $C_r = \frac{x + C}{2C} \cdot 100$"
eq_calidad_sigmoide = r"Modelo Sigmoide | Sigmoid Model: $C_r = \frac{100}{1 + 10^{-x/C}}$"

# --- Textos para los Títulos Superiores | Texts for the Suptitles ---
titulo_espanol = "Ecuación de la teoría de puntaje del equilibrio funcional"
titulo_ingles = "Score theory of the functional equilibrium equation"

# Construcción de los títulos apilados usando saltos de línea (\n)
titulo_completo_raiz = f"{titulo_espanol}\n{titulo_ingles}\n{eq_raiz}"
titulo_completo_log = f"{titulo_espanol}\n{titulo_ingles}\n{eq_log}"

# --- LIENZO 1: Ecuación de Raíces Cuadradas | CANVAS 1: Square Roots Equation ---
# Aumentamos el alto a 8 para acomodar el título de 3 líneas
fig1 = plt.figure(figsize=(16, 8))
# y=0.96 mueve el bloque de texto ligeramente hacia arriba
fig1.suptitle(titulo_completo_raiz, fontsize=16, fontweight='bold', y=0.96)

# Subplot Izquierdo: Raíz + Lineal | Left Subplot: Root + Linear
ax1 = fig1.add_subplot(1, 2, 1)
ax1.hist(p_lineal_raiz, bins=40, color='#3498db', edgecolor='black', alpha=0.7)
ax1.set_title(eq_calidad_lineal, fontsize=13, pad=15)
ax1.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax1.set_ylabel('Número de Individuos | Number of Individuals')

# Subplot Derecho: Raíz + Sigmoide | Right Subplot: Root + Sigmoid
ax2 = fig1.add_subplot(1, 2, 2)
ax2.hist(p_sigmoide_raiz, bins=40, color='#e74c3c', edgecolor='black', alpha=0.7)
ax2.set_title(eq_calidad_sigmoide, fontsize=13, pad=15)
ax2.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax2.set_ylabel('Número de Individuos | Number of Individuals')

# Ajustamos el límite superior (0.84) para que los histogramas no se encimen con el título
plt.tight_layout(rect=[0, 0.03, 1, 0.84])


# --- LIENZO 2: Ecuación Logarítmica | CANVAS 2: Logarithmic Equation ---
# Aumentamos el alto a 8 para acomodar el título de 3 líneas
fig2 = plt.figure(figsize=(16, 8))
fig2.suptitle(titulo_completo_log, fontsize=16, fontweight='bold', y=0.96)

# Subplot Izquierdo: Log + Lineal | Left Subplot: Log + Linear
ax3 = fig2.add_subplot(1, 2, 1)
ax3.hist(p_lineal_log, bins=40, color='#2ecc71', edgecolor='black', alpha=0.7)
ax3.set_title(eq_calidad_lineal, fontsize=13, pad=15)
ax3.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax3.set_ylabel('Número de Individuos | Number of Individuals')

# Subplot Derecho: Log + Sigmoide | Right Subplot: Log + Sigmoid
ax4 = fig2.add_subplot(1, 2, 2)
ax4.hist(p_sigmoide_log, bins=40, color='#9b59b6', edgecolor='black', alpha=0.7)
ax4.set_title(eq_calidad_sigmoide, fontsize=13, pad=15)
ax4.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax4.set_ylabel('Número de Individuos | Number of Individuals')

# Ajustamos el límite superior (0.84) para que los histogramas no se encimen con el título
plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# --- LIENZO 3: Análisis Tridimensional de Comportamiento Matemático | CANVAS 3: 3D Mathematical Behavior Analysis ---
# Creamos el tercer lienzo para las superficies 3D
fig3 = plt.figure(figsize=(18, 8))
fig3.suptitle("Superficie de Puntuación basada en Suma de Criterio Natural Estructural (-C a C)\nScoring Surface based on Sum of Structural Natural Criteria (-C to C)", fontsize=16, fontweight='bold', y=0.96)

# 1. Generación de la malla (Meshgrid) basada en el espacio natural de criterios
# En lugar de usar 0-100, partimos del espacio natural -C a C (ej. -4 a 4)
n_malla = np.linspace(1, tareas_totales, 50)
x_malla = np.linspace(-espacio_criterio, espacio_criterio, 50)
X_n, Y_x = np.meshgrid(n_malla, x_malla)

# 2. Transformación del criterio natural (x) a Calidad de Respuesta (µCr) usando el Modelo Lineal
Y_mu = ((Y_x + espacio_criterio) / (2.0 * espacio_criterio)) * 100.0

# 3. Cálculos Z para la Superficie (operaciones vectorizadas de numpy)
# Ecuación Raíces Cuadradas: g(µCr, n) = µCr * sqrt(µCr) * sqrt(n * (100/N))
Z_g = Y_mu * np.sqrt(Y_mu) * np.sqrt(X_n * (100.0 / tareas_totales))

# Ecuación Logarítmica: f(µCr, n) = µCr * sqrt(n) * log10(n + 1)
Z_f = Y_mu * np.sqrt(X_n) * np.log10(X_n + 1.0)

# Subplot Izquierdo 3D: Ecuación de Raíces Cuadradas | Left 3D Subplot: Square Roots Eq
ax5 = fig3.add_subplot(1, 2, 1, projection='3d')
# Usamos el colormap 'viridis' para facilitar la lectura de la topografía
surf1 = ax5.plot_surface(X_n, Y_mu, Z_g, cmap='viridis', edgecolor='none', alpha=0.9)
ax5.set_title(titulo_completo_raiz, fontsize=11, pad=15)
ax5.set_xlabel('\nCantidad de tareas completadas (n)\nNumber of completed tasks (n)')
ax5.set_ylabel('\nPromedio de Calidad de Respuestas (µCr)\nResponses Quality Mean (µCr)')
ax5.set_zlabel('\nPuntuación Final (P)\nFinal Score (P)')
fig3.colorbar(surf1, ax=ax5, shrink=0.5, aspect=10, pad=0.1)

# Subplot Derecho 3D: Ecuación Logarítmica | Right 3D Subplot: Logarithmic Eq
ax6 = fig3.add_subplot(1, 2, 2, projection='3d')
# Usamos el colormap 'plasma' para contrastar con la ecuación anterior
surf2 = ax6.plot_surface(X_n, Y_mu, Z_f, cmap='plasma', edgecolor='none', alpha=0.9)
ax6.set_title(titulo_completo_log, fontsize=11, pad=15)
ax6.set_xlabel('\nCantidad de tareas completadas (n)\nNumber of completed tasks (n)')
ax6.set_ylabel('\nPromedio de Calidad de Respuestas (µCr)\nResponses Quality Mean (µCr)')
ax6.set_zlabel('\nPuntuación Final (P)\nFinal Score (P)')
fig3.colorbar(surf2, ax=ax6, shrink=0.5, aspect=10, pad=0.1)

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# Desplegar ambos lienzos | Render both canvases
plt.show()