# F2 · Antenas OpenCellID + Mitsuba XML Piñero

**Estado**: ✅ Completada — 2026-04-24

---

## 1. Qué se hizo

### 1.1 Antenas

- Fuente: scraping OpenCellID DIC-2025 (`RFQs_Motorola_DIC25/ANTENAS_DB/data/exports/pinero_antenas_20251225_202437.csv`).
- Copia a F2 (`antenas_pinero_raw.csv`, 156 filas).
- Enriquecimiento con `enrich_antenas_pinero.py` análogo al de Recreo:
  - Centroide UP8: `-33.09270, -60.80047` (del mapa interactivo ANTENAS_DB)
  - Haversine distance + bearing deg respecto al centroide
  - MNC → operador (Personal 722/34, Movistar 722/7, Claro 722/310)
  - Bandas LTE estimadas por (tecnología, operador)

### 1.2 Geometría

- Converter `obj_to_mitsuba.py` genera XML Mitsuba 3 a partir del OBJ Blender + manifest.
- El XML NO inyecta los radio materials en sí (eso lo hace Sionna en runtime vía JSON mapping).
- BSDFs visuales solo para preview Mitsuba.
- Output principal: **`PINERO_UP8_scene.xml`** + **`material_mapping.json`** (2724 objects).

---

## 2. Hallazgos

### 2.1 Distribución de antenas Piñero

| Operador | N | % |
|---|:-:|:-:|
| Personal | 95 | 60.9% |
| Claro | 47 | 30.1% |
| Movistar | 14 | 9.0% |
| **TOTAL** | **156** | 100% |

| Tecnología | N | % |
|---|:-:|:-:|
| UMTS | 117 | 75.0% |
| GSM | 25 | 16.0% |
| **LTE** | **14** | **9.0%** |

### 2.2 ⚠ Gap identificado: pocas antenas LTE

**Solo 14 antenas LTE** en el dataset (vs ~100+ esperables para Piñero en 2026). Causas probables:

1. Scraping DIC-2025 desactualizado (los operadores AR desplegaron más LTE en 2025-2026).
2. Radio de scraping limitado.
3. OpenCellID subreporta cells LTE nuevas.

**Mitigación aplicada en F3**:
- Asumir **co-ubicación UMTS/LTE** (típica en AR: los eNodeB LTE se montan sobre infraestructura UMTS existente). Esto multiplica el set efectivo de TX LTE por 117/14 ≈ 8x, llevándolo a ~130 antenas LTE efectivas.
- Documentar el assumption en slide de metodología del anexo F5.
- Proponer re-scraping OpenCellID en F5 roadmap como paso de refinamiento.

### 2.3 Distribución espacial

| Distancia a UP8 | N antenas |
|---|:-:|
| 0-1 km | 9 |
| 1-3 km | 20 |
| 3-5 km | 28 |
| 5-10 km | 79 |
| 10+ km | 20 |
| **Dentro de 5 km** | **57** |

Antena más cercana: **Personal GSM** a **636 m** (bearing 4° — al norte). Cobertura celular en el perímetro inmediato es significativa; el análisis va a mostrar señal recibida alta en patios y exteriores.

### 2.4 Geometría escena

| Parámetro | Valor |
|---|:-:|
| bbox X | -284 a 476 m |
| bbox Y | -392 a 342 m |
| bbox Z | -0.4 a 13.3 m |
| Dimensiones | 760 × 735 × 13.7 m |
| Centroide local | (96, -25, 6.5) |
| N objetos | 2724 |
| N materiales RF | 5 (concrete 92%, metal 3%, glass 3%, ground 1%) |

Escena ~35% más grande que Recreo. Implica ~+30% tiempo de compute Colab (estimado 1.2 h vs 1 h Recreo).

---

## 3. Outputs

| Archivo | Propósito | Tamaño |
|---|---|---|
| `antenas_pinero_raw.csv` | 156 antenas OpenCellID sin enriquecer | 17 KB |
| `antenas_pinero_raw.json` | Mismo dataset, formato JSON | 87 KB |
| `antenas_pinero_enriched.csv` | Enriquecido con dist/bearing/operator/bands | ~25 KB |
| `antenas_pinero_summary.json` | Estadísticas de distribución | <1 KB |
| `enrich_antenas_pinero.py` | Script reproducible del enriquecimiento | 7 KB |
| `PINERO_UP8_scene.xml` | Escena Mitsuba 3 para Sionna RT | 2.5 KB |
| `material_mapping.json` | Mapping 2724 objetos → rf_material | ~100 KB |
| `scene_stats.json` | Métricas de la conversión OBJ→XML | <1 KB |
| `obj_to_mitsuba.py` | Script reproducible del converter | 9 KB |

---

## 4. Próximo paso (F3)

Escribir `F3_sionna_pinero/RF_ANALISIS_PINERO.ipynb` clonando la estructura de
`RFQ_Recreo/.../04_export/colab_notebook/RF_ANALISIS_FASE4_v4.12.ipynb` con:

1. Carga de `PINERO_UP8_scene.xml` y asignación de radio materials vía `material_mapping.json`.
2. TX set desde `antenas_pinero_enriched.csv` con co-ubicación UMTS/LTE.
3. Parámetros calibrados desde `F1_calibracion/parametros_calibrados.py`.
4. 3 bandas (B26/B28/B41) × 2 alturas (1.5 m / 7.5 m) = 6 radio maps.
5. Sweep de clutter `bajo/central/alto` para análisis de sensibilidad.
6. Output: `mediciones_sionna_coverage_pinero.csv` + `heatmaps_sionna_pinero.png`.

**Compute estimado**: ~1-1.5 h en Colab GPU T4.

---

**Autor**: Max Keczeli (BIS)
**Cliente**: Motorola Solutions Argentina — CP 01/26
