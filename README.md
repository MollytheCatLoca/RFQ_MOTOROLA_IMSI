# RFQ Motorola IMSI · Análisis RF Virtual

> Pipeline auxiliar de análisis de propagación celular sobre el Mini Penal A
> (Unidad Penitenciaria N°8 Piñero, Santa Fe) para la consultoría CP 01/26
> de Motorola Solutions Argentina.

---

## 🚀 Correr en Google Colab (1 click)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MollytheCatLoca/RFQ_MOTOROLA_IMSI/blob/main/pipeline_rf/notebook/RF_ANALISIS_PINERO.ipynb)

Abre el notebook directo en Colab. Cambia `Runtime → Change runtime type → T4 GPU` y ejecuta Cells 1 → 12 secuencialmente (~1.5 h total).

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
│   ├── parametros_calibrados.py      constantes calibradas en Recreo
│   └── scene_stats.json
│
├── notebook/
│   └── RF_ANALISIS_PINERO.ipynb      13 celdas · Colab
│
├── scripts/                         (scripts reproducibles de generación)
│   ├── parametros_calibrados.py
│   ├── enrich_antenas_pinero.py
│   └── obj_to_mitsuba.py
│
└── docs/
    ├── PLAN_5_FASES.md                         plan macro (F1→F5)
    ├── CALIBRACION_TRANSFERIDA_DE_RECREO.md    sustento de transferencia
    └── F2_README.md                            hallazgos antenas + geometría
```

---

## Contexto

El sitio de referencia (**UP N°9 Recreo**) contó con campaña de mediciones IDR
(abril 2026, 144 markers de campo), que permitió calibrar un modelo
Sionna RT 2.x two-slope LOS/NLOS alcanzando **MAE 2.90 dB en régimen NLOS**.

Piñero **no tiene campaña local**. Este pipeline transfiere las constantes
sistémicas de Recreo (propiedades 3GPP/ENACOM/ITU-R) a la geometría 3D
de Piñero, ajustando solo las constantes dependientes de sitio (clutter
peri-urbano, antenas OpenCellID locales).

Detalles en [`pipeline_rf/docs/CALIBRACION_TRANSFERIDA_DE_RECREO.md`](./pipeline_rf/docs/CALIBRACION_TRANSFERIDA_DE_RECREO.md).

---

## Flujo de 5 fases

| Fase | Estado | Descripción |
|:-:|:-:|---|
| **F1** | ✅ | Calibración transferida de Recreo (constantes sistémicas vs sitio) |
| **F2** | ✅ | Antenas OpenCellID Piñero + escena Mitsuba desde Blender v18 |
| **F3** | 🔄 | Ray tracing en Colab T4 (este repo + notebook) |
| **F4** | ⏳ | Validación cruzada Recreo ↔ Piñero + banda de incertidumbre |
| **F5** | ⏳ | Anexo técnico 30 slides A4 + PDF (terminología S1/S2) |

---

## Outputs esperados de F3

Al correr el notebook completo en Colab, se generan en `/content/outputs/`:

| Archivo | Tamaño | Propósito |
|---|:-:|---|
| `heatmaps_sionna_pinero.png` | ~3 MB | Figura compuesta 3×2 (bandas × alturas) |
| `mediciones_sionna_coverage_pinero.csv` | ~30 MB | Dataset espacial · input F4 |
| `sionna_stats_pinero.json` | <1 KB | Medianas/percentiles por banda |
| `rm_{B26,B28,B41}_z{1.5,7.5}.npy` | ~30 MB | Radio maps raw (checkpoint) |

Todo se empaqueta automáticamente en `PINERO_RF_outputs.zip` y se descarga
por la celda final del notebook.

---

## Reproducibilidad

Los scripts en `pipeline_rf/scripts/` son el pipeline completo local:

```bash
# 1. Enriquecer dataset antenas (necesita antenas_pinero_raw.csv de OpenCellID)
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
