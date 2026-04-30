# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 21:28:06 2026 | Creado en Martes 21 de Abril de 2026
a las 21:28:06 horas

@author: AXMAN y Gemini
"""

import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

# --- Configuración | Configuration ---
poblacion = 100_000 # population
tareas_totales = 20 # total_tasks
espacio_criterio = 4 # criteria_space: Representado como 'C' en las fórmulas | Represented as 'C' in the formulas

@njit
def calcular_puntuacion_final(media_calidad, completadas, total): # calculate_final_score
    """
    Aplica la fórmula de puntuación final: | Applies the final scoring formula: 
    P = Cr * sqrt(Cr) * sqrt(n * (100 / N))
    """
    # Factor de completitud | Completion factor
    factor_completitud = np.sqrt((completadas * 100.0) / total) # completion_factor
    return media_calidad * np.sqrt(media_calidad) * factor_completitud

# --- Simulación Acelerada con Numba | Accelerated Simulation with Numba ---
@njit(parallel=True)
def simular_poblacion(pob, tareas_tot, esp_crit):
    """
    Simula las puntuaciones usando Numba para compilar el código a C y paralelizar el bucle.
    Simulates scores using Numba to compile the code to C and parallelize the loop.
    """
    # Se pre-asignan matrices vacías por eficiencia matemática (más rápido que hacer .append())
    # Pre-allocate empty arrays for mathematical efficiency (faster than using .append())
    punt_finales_lineales = np.empty(pob, dtype=np.float64) # linear_final_scores
    punt_finales_sigmoides = np.empty(pob, dtype=np.float64) # sigmoid_final_scores

    # prange permite que el bucle se ejecute en múltiples núcleos del procesador
    # prange allows the loop to run across multiple processor cores
    for persona in prange(pob): # for person in range(population):
        # Simula tiradas de dados para 20 tareas (-4 a 4) -> 'x' en las fórmulas 
        # Simulate dice rolls for 20 tasks (-4 to 4) -> 'x' in formulas
        tiradas = np.random.randint(-esp_crit, esp_crit + 1, tareas_tot) # rolls
        
        # 1. Cálculo de Calidad Lineal | 1. Linear Quality Calculation
        # Fórmula: Cr = ((x + C) / 2C) * 100 | Formula: Cr = ((x + C) / 2C) * 100
        calidades_l = ((tiradas + esp_crit) / (2.0 * esp_crit)) * 100.0 # l_qualities
        media_l = np.mean(calidades_l) # l_mean
        
        # 2. Cálculo de Calidad Sigmoide | 2. Sigmoid Quality Calculation
        # Fórmula: Cr = 100 / (1 + 10**(-x/C)) | Formula: Cr = 100 / (1 + 10**(-x/C))
        calidades_s = 100.0 / (1.0 + 10.0**(-tiradas / esp_crit)) # s_qualities
        media_s = np.mean(calidades_s) # s_mean
        
        # Aleatorizar finalización (n) para modelar 'Mapeo del Error' 
        # Randomize completion (n) to model 'Mapping the Error'
        # Usamos np.random para que Numba lo soporte, sumando 1 al máximo para simular la misma lógica del código original
        completadas = np.random.randint(tareas_tot, tareas_tot + 1) # completed
        
        # Aplicar Fórmula de Puntuación Final | Apply Final Scoring Formula
        punt_finales_lineales[persona] = calcular_puntuacion_final(media_l, completadas, tareas_tot)
        punt_finales_sigmoides[persona] = calcular_puntuacion_final(media_s, completadas, tareas_tot)

    return punt_finales_lineales, punt_finales_sigmoides

# Ejecución de la simulación | Execution of the simulation
puntuaciones_finales_lineales, puntuaciones_finales_sigmoides = simular_poblacion(poblacion, tareas_totales, espacio_criterio)

# --- Visualización | Visualization ---
figura = plt.figure(figsize=(14, 7)) # fig
plt.style.use('seaborn-v0_8-whitegrid')

# Título Global: Ecuación de Puntuación Final | Global Title: Final Score Equation
plt.suptitle(r'Ecuación de Puntuación Final | Final Score Equation: $P = \mu_{C_r} \cdot \sqrt{\mu_{C_r}} \cdot \sqrt{n \cdot (100 \div N)}$', 
             fontsize=16, fontweight='bold', y=0.98)

# Gráfico 1: Distribución Lineal | Plot 1: Linear Distribution
plt.subplot(1, 2, 1)
plt.hist(puntuaciones_finales_lineales, bins=40, color='#3498db', edgecolor='black', alpha=0.7)
plt.title(r'Distribución de Puntuaciones: Modelo de Calidad Lineal' + '\n' + r'Linear Quality Model Distribution of Test Scores' + '\n' + r'$C_r = \frac{x + C}{2C} \cdot 100$', fontsize=14)
plt.xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
plt.ylabel('Número de Individuos | Number of Individuals')

# Gráfico 2: Distribución Sigmoide | Plot 2: Sigmoid Distribution
plt.subplot(1, 2, 2)
plt.hist(puntuaciones_finales_sigmoides, bins=40, color='#e74c3c', edgecolor='black', alpha=0.7)
plt.title(r'Distribución de Puntuaciones: Modelo de Calidad Sigmoide' + '\n' + r'Sigmoid Quality Model Distribution Of Test Scores' + '\n' + r'$C_r = \frac{100}{1 + 10^{-x/C}}$', fontsize=14)
plt.xlabel('Valor de la Puntuación Final (P) | Final Score Value (P)')
plt.ylabel('Número de Individuos | Number of Individuals')

# Ajustar diseño para hacer espacio para el título superior | Adjust layout to make room for suptitle
plt.tight_layout(rect=[0, 0.03, 1, 0.92]) 
plt.show()

# Imprimir Estadísticas Descriptivas | Print Descriptive Stats
print(f"--- Estadísticas para {poblacion} individuos | Statistics for {poblacion} individuals ---")
print(f"Puntuación Lineal | Linear Score  | Media | Mean: {np.mean(puntuaciones_finales_lineales):.2f} | Máx | Max: {np.max(puntuaciones_finales_lineales):.2f}")
print(f"Puntuación Sigmoide | Sigmoid Score | Media | Mean: {np.mean(puntuaciones_finales_sigmoides):.2f} | Máx | Max: {np.max(puntuaciones_finales_sigmoides):.2f}")