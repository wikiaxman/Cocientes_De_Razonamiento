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
poblacion = 1_000_000 # population
tareas_totales = 20 # total_tasks
espacio_criterio = 4 # criteria_space: Representado como 'C' en las fórmulas | Represented as 'C' in the formulas

@njit
def producto_de_raices(media_calidad, completadas, total): 
    """
    Aplica la fórmula de puntuación final basada en raíces: | Applies the root-based scoring formula: 
    g = Cr * sqrt(Cr) * sqrt(n * (100 / N))
    """
    factor_completitud = np.sqrt((completadas * 100.0) / total) 
    return media_calidad * np.sqrt(media_calidad) * factor_completitud
    
@njit
def producto_raiz_logaritmo(media_calidad, completadas): 
    """
    Aplica la fórmula de puntuación logarítmica parcial: | Applies the partial logarithmic scoring formula:
    f = Cr * sqrt(n) * log10(n + 1)
    """
    return media_calidad * np.sqrt(completadas) * np.log10(completadas + 1.0)

@njit
def producto_de_logaritmos(media_calidad, completadas, total):
    """
    Aplica la nueva fórmula de compresión logarítmica doble: | Applies the new double log compression formula:
    h = Cr * log10(Cr + 1) * log10((n * 100 / N) + 1)
    """
    completitud = (completadas * 100.0) / total
    return media_calidad * np.log10(media_calidad + 1.0) * np.log10(completitud + 1.0)

# --- Simulación Acelerada con Numba | Accelerated Simulation with Numba ---
@njit(parallel=True, nogil=True)
def simular_poblacion(pob, tareas_tot, esp_crit):
    """
    Simula las puntuaciones usando Numba para compilar el código a C y paralelizar el bucle.
    Simulates scores using Numba to compile the code to C and parallelize the loop.
    """
    punt_raices_lineales = np.empty(pob, dtype=np.float64) 
    punt_raices_sigmoides = np.empty(pob, dtype=np.float64) 
    punt_log_lineales = np.empty(pob, dtype=np.float64) 
    punt_log_sigmoides = np.empty(pob, dtype=np.float64) 
    punt_log_log_lineales = np.empty(pob, dtype=np.float64) 
    punt_log_log_sigmoides = np.empty(pob, dtype=np.float64) 

    for persona in prange(pob): 
        tiradas = np.random.randint(-esp_crit, esp_crit + 1, tareas_tot) # rolls
        
        # 1. Cálculo de Calidad Lineal | 1. Linear Quality Calculation
        calidades_l = ((tiradas + esp_crit) / (2.0 * esp_crit)) * 100.0 
        media_l = np.mean(calidades_l) 
        
        # 2. Cálculo de Calidad Sigmoide | 2. Sigmoid Quality Calculation
        calidades_s = 100.0 / (1.0 + 10.0**(-tiradas / esp_crit)) 
        media_s = np.mean(calidades_s) 
        
        completadas = np.random.randint(1, tareas_tot + 1) # completed
        
        # Aplicar ecuaciones | Apply equations
        punt_raices_lineales[persona] = producto_de_raices(media_l, completadas, tareas_tot)
        punt_raices_sigmoides[persona] = producto_de_raices(media_s, completadas, tareas_tot)
        
        punt_log_lineales[persona] = producto_raiz_logaritmo(media_l, completadas)
        punt_log_sigmoides[persona] = producto_raiz_logaritmo(media_s, completadas)
        
        punt_log_log_lineales[persona] = producto_de_logaritmos(media_l, completadas, tareas_tot)
        punt_log_log_sigmoides[persona] = producto_de_logaritmos(media_s, completadas, tareas_tot)

    return punt_raices_lineales, punt_raices_sigmoides, punt_log_lineales, punt_log_sigmoides, punt_log_log_lineales, punt_log_log_sigmoides

# Tiempo de inicio de la simulacíon | Initial time of the simulation
inicio = time.perf_counter_ns()

# Ejecución de la simulación | Execution of the simulation
p_lineal_raiz, p_sigmoide_raiz, p_lineal_log, p_sigmoide_log, p_lineal_log_log, p_sigmoide_log_log = simular_poblacion(poblacion, tareas_totales, espacio_criterio)

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
eq_log_log = r"$h(\mu_{C_r}, n) = \mu_{C_r} \cdot \log_{10}(\mu_{C_r} + 1) \cdot \log_{10}(n \cdot \frac{100}{N} + 1)$"
eq_calidad_lineal = r"Modelo Lineal | Linear Model: $C_r = \frac{x + C}{2C} \cdot 100$"
eq_calidad_sigmoide = r"Modelo Sigmoide | Sigmoid Model: $C_r = \frac{100}{1 + 10^{-x/C}}$"

# --- Textos para los Títulos Superiores | Texts for the Suptitles ---
titulo_espanol = "Ecuación de la teoría de puntaje del equilibrio funcional"
titulo_ingles = "Functional balance scoring theory equation"

# Construcción de los títulos apilados usando saltos de línea (\n)
titulo_completo_raiz = f"{titulo_espanol}\n{titulo_ingles}\n{eq_raiz}"
titulo_completo_log = f"{titulo_espanol}\n{titulo_ingles}\n{eq_log}"
titulo_completo_log_log = f"{titulo_espanol}\n{titulo_ingles}\n{eq_log_log}"

# --- LIENZO 1: Ecuación de Raíces Cuadradas | CANVAS 1: Square Roots Equation ---
fig1 = plt.figure(figsize=(16, 8))
fig1.suptitle(titulo_completo_raiz, fontsize=16, fontweight='bold', y=0.96)

ax1 = fig1.add_subplot(1, 2, 1)
ax1.hist(p_lineal_raiz, bins=40, color='#3498db', edgecolor='black', alpha=0.7)
ax1.set_title(eq_calidad_lineal, fontsize=13, pad=15)
ax1.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax1.set_ylabel('Número de Individuos | Number of Individuals')

ax2 = fig1.add_subplot(1, 2, 2)
ax2.hist(p_sigmoide_raiz, bins=40, color='#e74c3c', edgecolor='black', alpha=0.7)
ax2.set_title(eq_calidad_sigmoide, fontsize=13, pad=15)
ax2.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax2.set_ylabel('Número de Individuos | Number of Individuals')

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# --- LIENZO 2: Ecuación Logarítmica | CANVAS 2: Logarithmic Equation ---
fig2 = plt.figure(figsize=(16, 8))
fig2.suptitle(titulo_completo_log, fontsize=16, fontweight='bold', y=0.96)

ax3 = fig2.add_subplot(1, 2, 1)
ax3.hist(p_lineal_log, bins=40, color='#2ecc71', edgecolor='black', alpha=0.7)
ax3.set_title(eq_calidad_lineal, fontsize=13, pad=15)
ax3.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax3.set_ylabel('Número de Individuos | Number of Individuals')

ax4 = fig2.add_subplot(1, 2, 2)
ax4.hist(p_sigmoide_log, bins=40, color='#9b59b6', edgecolor='black', alpha=0.7)
ax4.set_title(eq_calidad_sigmoide, fontsize=13, pad=15)
ax4.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax4.set_ylabel('Número de Individuos | Number of Individuals')

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# --- LIENZO 3: Producto de Logaritmos | CANVAS 3: Product of Logarithms ---
fig3 = plt.figure(figsize=(16, 8))
fig3.suptitle(titulo_completo_log_log, fontsize=16, fontweight='bold', y=0.96)

ax5 = fig3.add_subplot(1, 2, 1)
ax5.hist(p_lineal_log_log, bins=40, color='#e67e22', edgecolor='black', alpha=0.7)
ax5.set_title(eq_calidad_lineal, fontsize=13, pad=15)
ax5.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax5.set_ylabel('Número de Individuos | Number of Individuals')

ax6 = fig3.add_subplot(1, 2, 2)
ax6.hist(p_sigmoide_log_log, bins=40, color='#16a085', edgecolor='black', alpha=0.7)
ax6.set_title(eq_calidad_sigmoide, fontsize=13, pad=15)
ax6.set_xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
ax6.set_ylabel('Número de Individuos | Number of Individuals')

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# --- LIENZO 4: Análisis Tridimensional de Comportamiento Matemático | CANVAS 4: 3D Mathematical Behavior Analysis ---
fig4 = plt.figure(figsize=(18, 8))
fig4.suptitle("Superficie de Puntuación basada en Suma de Criterio Natural Estructural (-C a C)\nScoring Surface based on Sum of Structural Natural Criteria (-C to C)", fontsize=16, fontweight='bold', y=0.96)

n_malla = np.linspace(1, tareas_totales, 50)
x_malla = np.linspace(-espacio_criterio, espacio_criterio, 50)
X_n, Y_x = np.meshgrid(n_malla, x_malla)
Y_mu = ((Y_x + espacio_criterio) / (2.0 * espacio_criterio)) * 100.0

Z_g = Y_mu * np.sqrt(Y_mu) * np.sqrt(X_n * (100.0 / tareas_totales))
Z_f = Y_mu * np.sqrt(X_n) * np.log10(X_n + 1.0)

ax7 = fig4.add_subplot(1, 2, 1, projection='3d')
surf1 = ax7.plot_surface(X_n, Y_mu, Z_g, cmap='viridis', edgecolor='none', alpha=0.9)
ax7.set_title(titulo_completo_raiz, fontsize=11, pad=15)
ax7.set_xlabel('\nCantidad de tareas respondidas (n)\nNumber of answered tasks (n)')
ax7.set_ylabel('\nPromedio de Calidad de Respuestas (µCr)\nResponses Quality Mean (µCr)')
ax7.set_zlabel('\nPuntuación Final (P)\nFinal Score (P)')
fig4.colorbar(surf1, ax=ax7, shrink=0.5, aspect=10, pad=0.1)

ax8 = fig4.add_subplot(1, 2, 2, projection='3d')
surf2 = ax8.plot_surface(X_n, Y_mu, Z_f, cmap='plasma', edgecolor='none', alpha=0.9)
ax8.set_title(titulo_completo_log, fontsize=11, pad=15)
ax8.set_xlabel('\nCantidad de tareas respondidas (n)\nNumber of answered tasks (n)')
ax8.set_ylabel('\nPromedio de Calidad de Respuestas (µCr)\nResponses Quality Mean (µCr)')
ax8.set_zlabel('\nPuntuación Final (P)\nFinal Score (P)')
fig4.colorbar(surf2, ax=ax8, shrink=0.5, aspect=10, pad=0.1)

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# --- LIENZO 5: Superficie 3D de Producto de Logaritmos | CANVAS 5: Product of Logarithms 3D Surface ---
fig5 = plt.figure(figsize=(10, 8))
fig5.suptitle("Superficie de Puntuación basada en Suma de Criterio Natural Estructural (-C a C)\nScoring Surface based on Sum of Structural Natural Criteria (-C to C)", fontsize=16, fontweight='bold', y=0.96)

# Cálculo de Z para la nueva ecuación h(µCr, n)
Z_h = Y_mu * np.log10(Y_mu + 1.0) * np.log10((X_n * (100.0 / tareas_totales)) + 1.0)

ax9 = fig5.add_subplot(1, 1, 1, projection='3d')
surf3 = ax9.plot_surface(X_n, Y_mu, Z_h, cmap='magma', edgecolor='none', alpha=0.9)
ax9.set_title(titulo_completo_log_log, fontsize=11, pad=15)
ax9.set_xlabel('\nCantidad de tareas respondidas (n)\nNumber of answered tasks (n)')
ax9.set_ylabel('\nPromedio de Calidad de Respuestas (µCr)\nResponses Quality Mean (µCr)')
ax9.set_zlabel('\nPuntuación Final (P)\nFinal Score (P)')
fig5.colorbar(surf3, ax=ax9, shrink=0.5, aspect=10, pad=0.1)

plt.tight_layout(rect=[0, 0.03, 1, 0.84])

# Desplegar los cinco lienzos | Render all five canvases
plt.show()