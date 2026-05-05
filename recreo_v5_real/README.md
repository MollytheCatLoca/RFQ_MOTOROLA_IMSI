# Recreo v5.0 REAL · Sionna Ray Tracing con data DXF real

> Pipeline auxiliar para regenerar heatmaps RF de UP9 Recreo usando **57 edificios reales** derivados de los planos DWG entregados por SPF Santa Fe (2026-04-28), reemplazando los 20 edificios sintéticos a ojo del v4.12.

---

## 🚀 Correr en Google Colab (1 click)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MollytheCatLoca/RFQ_MOTOROLA_IMSI/blob/main/recreo_v5_real/notebook/RF_ANALISIS_FASE4_v5.0_REAL.ipynb)

**Pasos**:
1. Click en el badge → abre el notebook directamente en Colab
2. `Runtime → Change runtime type → Hardware accelerator: GPU (T4 o L4)`
3. `Runtime → Run all` → ~15-25 min

El notebook clona automáticamente este repo y carga los inputs desde `recreo_v5_real/inputs/`. **No necesitás Google Drive** (a menos que quieras outputs persistentes).

---

## 📂 Estructura

```
recreo_v5_real/
├── notebook/
│   └── RF_ANALISIS_FASE4_v5.0_REAL.ipynb   ← notebook editado
├── inputs/                                  ← datasets que carga el notebook
│   ├── up9_buildings_s1_calado.json        ⭐ 57 edif reales (vs 20 sintéticos v4.12)
│   ├── antenas_recreo_enriched.csv         antenas telco (sin cambios)
│   ├── mediciones_raw.csv                  IDR ground truth (sin cambios)
│   ├── mediciones_sinteticas_floor_summary.csv  reference (sin cambios)
│   └── mediciones_sinteticas_altura_summary.csv reference (sin cambios)
├── outputs/                                 ← se llena al correr el notebook
│   └── (heatmaps_sionna_REAL.png, mediciones_sionna_coverage_REAL.csv, etc.)
├── README.md                                este archivo
└── RUNBOOK.md                               troubleshooting + diferencias técnicas
```

---

## 📊 Cambios vs v4.12 sintético

| Aspecto | v4.12 sintético | v5.0 REAL |
|---|---|---|
| Edificios | 20 rectángulos (a ojo en satelital) | 57 polígonos del DWG real |
| Geometría por edif | 4 corners | 4-50 vértices (forma real) |
| Origen GPS | -31.509878, -60.721272 (estimado) | -31.510037, -60.721543 (calibrado satelital) |
| Garitas | NO | SÍ (26 puntos vigilancia) |
| muro_db | 25dB todos | 12-25dB diferenciado por tipo |
| altura_m | 6m todos | 4-8m por tipo (pab=6, gob=7, garita=8) |
| Sub-unidades | confusión (UP9 entero) | clarificado (4 SUs en master, solo SU1 construida) |

---

## 🔗 Trazabilidad

- **Source DWG**: planos UP9 SPF Santa Fe (2026-04-28)
- **Pipeline DXF→JSON**: ezdxf + shapely buffer+union + filtro radio 45m
- **Calibración georef**: editor Leaflet manual sobre satélite Google Maps (anchor + rotación + flipY)
- **Repositorio assets completos**: ver project Mac local en `RFQ_Recreo/04_ejecucion/auxiliares/_assets/planos_recreo/`

---

## 📋 Outputs esperados

Cuando termine la corrida en Colab, en `recreo_v5_real/outputs/`:
- `heatmaps_sionna_REAL.png` ⭐ heatmap RF (6 paneles · 2 alturas × 3 bandas)
- `mediciones_sionna_coverage_REAL.csv` puntos × bandas con dBm
- `validacion_sionna_vs_idr_REAL.csv` correlación con ground truth IDR

Comparar contra `heatmaps_sionna.png` (sintético v4.12) para ver el impacto de la geometría real.

---

## ⚠️ Troubleshooting

Ver `RUNBOOK.md` para detalles. Issues conocidos:
- `extrude_polygon engine='earcut'` → instalar `mapbox-earcut` (cell 1)
- `Polygon is not valid` → buffer(0) auto-fix en cell 10
- Out-of-memory en T4 → bajar `samples_per_tx` de 2e6 a 5e5
