# Runbook · Sionna v5.0 REAL · Heatmaps con data DXF real

**Objetivo**: regenerar `heatmaps_sionna.png` y `mediciones_sionna_coverage.csv` usando el modelo real de UP9 (57 edificios derivados de los DWG SPF Santa Fe), reemplazando los 20 sintéticos de v4.12.

---

## Pre-requisitos

- **Cuenta Google** con Drive
- **Sesión Colab con GPU** (free tier sirve · T4 o L4)
- ~30 min de tiempo de cómputo (escala con building count)

---

## Pasos

### 1. Subir inputs a Drive

Copia los **6 archivos** de esta carpeta (`sionna_run_v5_REAL/`) a tu Drive en:

```
Drive/Sionna_RF/v5_real/
├── RF_ANALISIS_FASE4_v5.0_REAL.ipynb       ← notebook principal
├── up9_buildings_s1_calado.json            ⭐ NUEVO (57 edif reales)
├── antenas_recreo_enriched.csv             (sin cambios)
├── mediciones_raw.csv                      (sin cambios)
├── mediciones_sinteticas_floor_summary.csv (sin cambios)
└── mediciones_sinteticas_altura_summary.csv (sin cambios)
```

### 2. Abrir notebook en Colab

```
File → Open notebook → Google Drive → RF_ANALISIS_FASE4_v5.0_REAL.ipynb
```

### 3. Configurar GPU

```
Runtime → Change runtime type → Hardware accelerator: GPU (T4 o L4)
```

### 4. Editar `DRIVE_BASE` en celda 4

Asegurarse que apunta a tu carpeta:
```python
DRIVE_BASE = Path('/content/drive/MyDrive/Sionna_RF/v5_real/')
```

### 5. Run All

```
Runtime → Run all
```

**Tiempos esperados**:
- Setup + install Sionna: 2-3 min
- Mount drive + load: 30 seg
- Build mesh scene (57 edif): 1-2 min (vs 30 seg con 20 edif sintéticos)
- Test run 1 banda: ~30 seg
- Full run 6 maps: 5-10 min
- Export: 1 min
- **Total: ~15-25 min**

### 6. Outputs esperados

En Drive `Sionna_RF/v5_real/sionna_outputs/`:
- `heatmaps_sionna_REAL.png` ⭐ (6 paneles · 2 alturas × 3 bandas)
- `mediciones_sionna_coverage_REAL.csv` (puntos × bandas con dBm)
- `validacion_sionna_vs_idr_REAL.csv` (correlación con ground truth)

### 7. Bajar a local

Copiar los outputs a:
```
auxiliares/analisis_espectro_rf/05_analisis_rf/sionna_outputs_v5_REAL/
```

---

## Diferencias técnicas vs v4.12

| Aspecto | v4.12 (sintético) | v5.0 (real) |
|---|---|---|
| Edificios | 20 (rectángulos a ojo) | 57 (polígonos DWG · multi-vértice) |
| Geometría | 4 corners por edif | 4-50 vértices por edif (forma real) |
| Origen GPS | -31.509878, -60.721272 | -31.510037, -60.721543 (calibrado) |
| Total mesh verts | ~80 | ~200-500 (depende complejidad) |
| Garitas modeladas | NO | SÍ (26 puntos × 5×5×8m) |
| Sub-unidades | confusión (1 SU planeada como toda UP9) | clarificado (4 SUs en master plan, solo SU1 construida) |
| muro_db | 25dB (todos) | 12-25dB (variado por tipo: hormigón=25, mampostería=12-15) |
| altura_m | 6m (todos) | 4-8m (variado: pab=6, gob=7, garita=8) |

---

## Troubleshooting

### "trimesh.creation.extrude_polygon engine='earcut' error"
Asegurate que la celda 1 instaló mapbox-earcut:
```
!pip install mapbox-earcut shapely trimesh
```

### "Polygon is not valid" para algún edificio
Los polígonos del editor manual pueden tener self-intersections menores. La celda 10 usa `poly.buffer(0)` para auto-fix. Si hay errores raros, revisar el edificio específico en `up9_buildings_s1_calado.json`.

### "Out of memory" en RadioMapSolver
57 edificios + ground = más mesh que 20. Si Colab T4 no aguanta:
- Reducir `samples_per_tx` de 2e6 a 5e5
- O usar L4 GPU (Pro plan)

### Coverage maps "vacíos" o todo en min_dbm
- Verificar que `to_enu()` da valores razonables (debería estar centrado cerca de origen)
- Verificar que las antenas están dentro del bbox de la escena
- Probar test run 1 banda primero (cell 8a)

---

## Validación de output

Una vez generado el heatmap real, comparar contra:
1. **Heatmap sintético previo**: `heatmaps_sionna.png` (Apr 17)
2. **IDR ground truth**: 3 puntos MS1/MS2/MS3 reales
3. **Modelo analítico FSPL**: cálculo manual desde antenas top-5

**Esperado**: el heatmap real debería:
- Mostrar el footprint del edificio real (no rectángulos)
- Mejor correlación con MS3 (interior)
- Más sombras de RF detrás de pabellones (multi-vertex polygons proyectan sombras más complejas)
- Diferenciación por banda (B28 700 MHz penetra más que B41 2.6 GHz)
