#!/usr/bin/env python3
"""
Parámetros calibrados del pipeline BIS validado, transferidos a Piñero.

Consumido por los scripts de F2 (antenas + Mitsuba) y F3 (Sionna RT).

Separa las constantes en 3 grupos:
  - SYSTEMIC_*  → transferibles directas desde DB propia BIS (propiedades regulatorias/3GPP/ITU)
  - SITE_PINERO_*  → específicas del sitio Piñero (clutter, antenas locales, polígono)
  - SWEEP_*  → rangos de sensibilidad para análisis de incertidumbre

Uso:
    from parametros_calibrados import EIRP_DBM, BAND_TO_TECH, BAND_FREQ_MHZ, \\
        NLOS_OFFSET_DB, CLUTTER_LOSS_DB_PINERO_FLOOR, SIONNA_SOLVER_CONFIG

Referencia: ver CALIBRACION_BASE_DATOS_BIS.md en esta misma carpeta.
"""
from __future__ import annotations

# ============================================================================
# GRUPO 1 · Constantes sistémicas (transferidas 1:1 desde DB propia BIS)
# Fuentes: ENACOM Res. 302/2022, 3GPP TS 25.104, ITU-R M.2412, ITU-R P.2040-3
# ============================================================================

SYSTEMIC_EIRP_DBM = {
    "Personal":    {"LTE": 46, "UMTS": 44, "GSM": 42},
    "Claro":       {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Movistar":    {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Desconocido": {"LTE": 43, "UMTS": 42, "GSM": 40},
}

SYSTEMIC_BAND_FREQ_MHZ = {
    "B2":  1960.0,    # PCS
    "B4":  2132.5,    # AWS
    "B7":  2655.0,    # 2.6 GHz FDD
    "B25": 1962.5,    # Extended PCS
    "B26": 876.5,     # 850 MHz (compartido LTE/UMTS/GSM)
    "B28": 780.5,     # APT 700 LTE
    "B41": 2593.0,    # TDD 2.6 GHz
    "B66": 2155.0,    # Extended AWS
}

SYSTEMIC_BAND_TO_TECH = {
    "B2":  ["LTE"],
    "B4":  ["LTE"],
    "B7":  ["LTE"],
    "B25": ["LTE"],
    "B26": ["LTE", "UMTS", "GSM"],
    "B28": ["LTE"],
    "B41": ["LTE"],
    "B66": ["LTE"],
}

SYSTEMIC_PRIORITY_BANDS = ["B26", "B28", "B41"]  # Mismas prioritarias que DB BIS para permitir comparativa

SYSTEMIC_NLOS_OFFSET_DB = 41.2           # ITU-R M.2412 App B · calibrado empíricamente DB BIS
SYSTEMIC_LOS_NLOS_THRESHOLD_DB = 30.0    # |delta_raw| < 30 dB → LOS

SYSTEMIC_ANTENNA_MISPOINTING_DB = 5.0    # Antenas urbanas apuntan al core, no al penal
SYSTEMIC_H_TX_MACRO_M = 25.0             # Altura típica torre macro AR

# Materiales ITU-R P.2040-3 (ya embebidos en UP9_RF_manifest.json)
SYSTEMIC_MATERIALS = {
    "concrete": {"epsilon_r": 5.31, "sigma": 0.0326, "thickness": 0.25},
    "brick":    {"epsilon_r": 3.75, "sigma": 0.0380, "thickness": 0.20},
    "glass":    {"epsilon_r": 6.27, "sigma": 0.0043, "thickness": 0.008},
    "metal":    {"epsilon_r": 1.00, "sigma": 1e7,    "thickness": 0.01},
    "ground_wet": {"epsilon_r": 30.0, "sigma": 0.15,  "thickness": 1.0},
    "ground_dry": {"epsilon_r": 3.0,  "sigma": 0.001, "thickness": 1.0},
}

# ============================================================================
# GRUPO 2 · Configuración Sionna RT (parámetros de solver, no dependen del sitio)
# ============================================================================

SIONNA_SOLVER_CONFIG = {
    "max_depth": 5,
    "samples_per_tx": 1_000_000,
    "cell_size": (2.0, 2.0),        # metros
    "diffraction": True,
    "edge_diffraction": True,
    "specular_reflection": True,
    "diffuse_reflection": False,    # evita sobreestimación en ambiente cerrado
    "refraction": True,
}

SIONNA_ANALYSIS_HEIGHTS_M = [1.5, 7.5]  # antropométrico + nivel pabellón 2

# ============================================================================
# GRUPO 3 · Constantes específicas Piñero (ajustadas dcasos comparables)
# ============================================================================

# Sweep de sensibilidad para clutter loss. Central = recomendación base.
SITE_PINERO_CLUTTER_FLOOR_DB = {
    "bajo":    15.0,    # peri-urbano, cota inferior
    "central": 20.0,    # recomendación base (entre entorno semi-rural y urbano denso)
    "alto":    25.0,    # heredado DB BIS (cota superior, conservador)
}

SITE_PINERO_CLUTTER_ALTURA_DB = {
    "bajo":    7.0,     # LoS más clara que sitio de referencia BIS (menos arboleda alta)
    "central": 8.5,
    "alto":    10.0,    # heredado DB BIS
}

# Centroide del Mini Penal A - PENDIENTE extracción en F2 del manifest Blender
SITE_PINERO_CENTROID_LATLON = None  # TODO F2

# Polígono Mini Penal A - PENDIENTE derivación en F2
SITE_PINERO_POLYGON = None  # TODO F2

# Catálogo antenas OpenCellID - PENDIENTE query en F2
SITE_PINERO_ANTENNAS_CSV = "../F2_antenas_y_mitsuba/antenas_pinero_enriched.csv"  # TODO F2

# ============================================================================
# GRUPO 4 · MAE proyectado (para banda de incertidumbre reportada en F4/F5)
# ============================================================================

MAE_sitio de referencia BIS_VALIDATED = {
    "analitico":              9.30,
    "sionna_raw":            31.41,
    "sionna_calibrado_global":  6.59,
    "sionna_calibrado_NLOS":    2.90,
    "sionna_calibrado_LOS":    12.73,
}

MAE_PINERO_PROJECTED = {
    # Cotas proyectadas por acumulación de incertidumbres (ver sección 5.2 del MD)
    "NLOS_low":   6.0,
    "NLOS_high":  8.0,
    "global_low": 9.0,
    "global_high": 11.0,
}

# ============================================================================
# Util helpers
# ============================================================================

def get_clutter_loss(z_m: float, scenario: str = "central") -> float:
    """Devuelve el clutter loss en dB para una altura y escenario dado."""
    if z_m <= 2.0:
        return SITE_PINERO_CLUTTER_FLOOR_DB[scenario]
    elif z_m <= 8.0:
        return SITE_PINERO_CLUTTER_ALTURA_DB[scenario]
    else:
        # Por encima de 8 m, interpolación lineal hacia 0 dB en h_tx (25 m)
        c8 = SITE_PINERO_CLUTTER_ALTURA_DB[scenario]
        alpha = min(1.0, (z_m - 8.0) / (SYSTEMIC_H_TX_MACRO_M - 8.0))
        return c8 * (1 - alpha)


def get_eirp_dbm(operator: str, technology: str) -> float:
    """Lookup EIRP seguro con fallback a Desconocido."""
    op_dict = SYSTEMIC_EIRP_DBM.get(operator, SYSTEMIC_EIRP_DBM["Desconocido"])
    return op_dict.get(technology, 40.0)


def is_band_compatible_with_tech(band: str, tech: str) -> bool:
    """¿Puede emitirse tecnología `tech` en banda `band` en Argentina?"""
    return tech in SYSTEMIC_BAND_TO_TECH.get(band, [])


if __name__ == "__main__":
    # Smoke test para verificar carga y consistencia
    print("=" * 70)
    print("Parámetros calibrados F1 — Análisis RF Virtual Piñero")
    print("=" * 70)
    print(f"Bandas prioritarias: {SYSTEMIC_PRIORITY_BANDS}")
    print(f"NLOS offset: +{SYSTEMIC_NLOS_OFFSET_DB} dB (ITU-R M.2412 App B)")
    print(f"Clutter floor sweep: {SITE_PINERO_CLUTTER_FLOOR_DB}")
    print(f"Clutter altura sweep: {SITE_PINERO_CLUTTER_ALTURA_DB}")
    print(f"MAE esperado NLOS Piñero: {MAE_PINERO_PROJECTED['NLOS_low']}-{MAE_PINERO_PROJECTED['NLOS_high']} dB")
    print(f"  (vs {MAE_sitio de referencia BIS_VALIDATED['sionna_calibrado_NLOS']} dB validado en sitio de referencia BIS)")
    print()
    print("Smoke tests:")
    assert is_band_compatible_with_tech("B26", "GSM"), "B26 debe soportar GSM"
    assert not is_band_compatible_with_tech("B41", "GSM"), "B41 TDD solo LTE"
    assert get_eirp_dbm("Personal", "LTE") == 46, "Personal LTE debe ser 46 dBm"
    assert get_eirp_dbm("Movistar", "GSM") == 42, "Movistar GSM debe ser 42 dBm"
    assert get_clutter_loss(1.5, "central") == 20.0, "Clutter central z=1.5 debe ser 20 dB"
    assert get_clutter_loss(7.5, "central") == 8.5, "Clutter central z=7.5 debe ser 8.5 dB"
    assert 0 <= get_clutter_loss(25.0, "central") < 1.0, "Clutter a h_tx debe ser ~0"
    print("  ✅ Todos los tests pasaron")
