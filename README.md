# RFQ Motorola IMSI · Análisis RF Virtual

> Pipeline auxiliar de análisis de propagación celular sobre el Mini Penal A
> (Unidad Penitenciaria N°8 Piñero, Santa Fe) para la consultoría CP 01/26
> de Motorola Solutions Argentina.

---

## 🚀 Correr en Google Colab (1 click)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MollytheCatLoca/RFQ_MOTOROLA_IMSI/blob/main/pipeline_rf/notebook/RF_ANALISIS_PINERO.ipynb)

Abre el notebook directo en Colab. Cambia `Runtime → Change runtime type → T4 GPU` y ejecuta las celdas secuencialmente (~1.5 h total).

---

## Estructura del repo

```
pipeline_rf/
├── inputs/                          (3.2 MB · lo que consume Colab)
│   ├── PINERO_UP8_scene.xml          escena Mitsuba 3
│   ├── UP9_unidad_alto_perfil.obj    geometría 3D (2724 objetos)
│   ├── UP9_unidad_alto_perfil.mtl
│   ├── UP9_RF_manifest.json          ITU-R P.2040 materials
│   ├── UP9_objects_rf.csv            lookup object → material
│   ├── material_mapping.json         mapping compacto runtime
│   ├── antenas_pinero_enriched.csv   156 antenas OpenCellID
│   ├── parametros_calibrados.py      constantes calibradas (DB propia BIS)
│   └── scene_stats.json
│
├── notebook/
│   └── RF_ANALISIS_PINERO.ipynb      notebook Colab
│
├── scripts/                         (scripts reproducibles de generación)
│   ├── parametros_calibrados.py
│   ├── enrich_antenas_pinero.py
│   └── obj_to_mitsuba.py
│
└── docs/
    ├── PLAN_5_FASES.md                 plan macro (F1→F5)
    ├── CALIBRACION_BASE_DATOS_BIS.md   sustento metodológico de calibración
    └── F2_README.md                    hallazgos antenas + geometría
```

---

## Contexto

Este pipeline aplica ray tracing RF de alta fidelidad (Sionna RT sobre GPU T4 en
Google Colab) para caracterizar el entorno electromagnético del Mini Penal A
antes del diseño del sistema integral de inhibición.

La calibración del modelo se sustenta en la **base de datos propia BIS de
mediciones RF en establecimientos penitenciarios argentinos**, incluyendo
sitios relevados en la provincia de Santa Fe. Los parámetros de corrección
(offset two-slope NLOS según ITU-R M.2412, constantes de clutter peri-urbano,
factores de antena sectorial 3GPP) fueron validados empíricamente contra
mediciones de campo IDR.

Detalles en [`pipeline_rf/docs/CALIBRACION_BASE_DATOS_BIS.md`](./pipeline_rf/docs/CALIBRACION_BASE_DATOS_BIS.md).

---

## Flujo de 5 fases

| Fase | Estado | Descripción |
|:-:|:-:|---|
| **F1** | ✅ | Calibración basada en DB propia BIS (constantes sistémicas vs sitio) |
| **F2** | ✅ | Antenas OpenCellID Piñero + escena Mitsuba desde Blender v18 |
| **F3** | ✅ | Ray tracing en Colab T4 · 6 mapas generados · 194k puntos |
| **F4** | 🔄 | Calibración two-slope + banda de incertidumbre |
| **F5** | ⏳ | Anexo técnico 30 slides A4 + PDF (terminología S1/S2) |

---

## Outputs esperados

Al correr el notebook completo en Colab, se generan en `/content/outputs/`:

| Archivo | Tamaño | Propósito |
|---|:-:|---|
| `heatmaps_sionna_pinero.png` | ~3 MB | Figura compuesta 3×2 (bandas × alturas) |
| `mediciones_sionna_coverage_pinero.csv` | ~14 MB | Raster espacial (194k puntos) |
| `sionna_stats_pinero.json` | <1 KB | Medianas/percentiles por banda |
| `rm_{B26,B28,B41}_z{1.5,7.5}.npy` | ~12 MB | Radio maps raw (checkpoint) |

Todo se empaqueta automáticamente en `PINERO_RF_outputs.zip` y se descarga
por la celda final del notebook.

---

## Reproducibilidad

Los scripts en `pipeline_rf/scripts/` son el pipeline completo local:

```bash
# 1. Enriquecer dataset antenas
python3 scripts/enrich_antenas_pinero.py

# 2. Convertir geometría Blender → Mitsuba XML
python3 scripts/obj_to_mitsuba.py

# 3. Verificar constantes calibradas (smoke test)
python3 scripts/parametros_calibrados.py

# 4. Subir + correr notebook en Colab (GPU requerida)
```

---

## Referencias técnicas

- **Sionna RT**: https://nvlabs.github.io/sionna/
- **ITU-R P.2040-3** — Effects of building materials on radiowave propagation
- **ITU-R M.2412** — Guidelines for IMT-2020 (two-slope LOS/NLOS reference)
- **OpenCellID**: https://www.opencellid.org/
- **ENACOM Res. 302/2022** — asignaciones espectrales AR

---

## Licencia y confidencialidad

Repositorio de trabajo técnico · BIS Integraciones · Max Keczeli.
Los datos de antenas provienen de OpenCellID (CC-BY-SA 4.0).
La geometría 3D es modelo simplificado interno — no contiene planos operativos ni información restringida.
