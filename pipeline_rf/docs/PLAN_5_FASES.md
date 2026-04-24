# Análisis RF Virtual — Mini Penal A · UP N°8 Piñero

> Proyecto auxiliar análogo al pipeline BIS validado (`DB propia BIS · `),
> aplicado a la geometría del Mini Penal A de Piñero.
> Autor: Max Keczeli (BIS) · Arranque: 2026-04-24

---

## 1. Propósito

Producir un anexo técnico RF de **30 slides A4 + PDF** sobre la cobertura celular de referencia
en el Mini Penal A (UP N°8 Piñero), para acompañar la propuesta económica CP 01/26 y la
narrativa técnica V1.1 (`08_Pliego_PROPUESTA_BIS_MOTOROLA/BIS_MOTOROLA_Sistema_Inhibicion_Pinero_V1_1.docx`).

**Producto esperado**: `F5_anexo_pinero/BIS_MOTOROLA_ANALISIS_RF_PINERO_ABR26.pdf`

---

## 2. Particularidad metodológica

A diferencia de la DB propia BIS (que tuvo campaña IDR con 144 markers de campo), Piñero **NO tiene
mediciones locales**. La metodología aplicada usa los 144 markers de la DB propia BIS como **calibración
base transferida** bajo justificación física/regulatoria documentada en F1.

Consecuencia: el MAE esperado en Piñero es **mayor que el de la DB propia BIS** (+3-5 dB sobre el 2.90 dB
NLOS de la DB propia BIS), y el anexo lo publica explícitamente como banda de incertidumbre ampliada.

---

## 3. Pipeline 5 fases

```
┌─────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐
│  F1     │→ │  F2          │→ │  F3      │→ │  F4       │→ │  F5      │
│Calibr.  │  │Antenas+      │  │Sionna RT │  │Validación │  │Anexo 30  │
│sitio de referencia BIS→  │  │Mitsuba XML   │  │Piñero    │  │cruzada    │  │slides+   │
│Piñero   │  │              │  │          │  │           │  │PDF       │
└─────────┘  └──────────────┘  └──────────┘  └───────────┘  └──────────┘
   1d            1-2d             1-2d            1d            2d
```

### F1 — Calibración transferida de la DB propia BIS ✅ en curso
Documentar qué constantes del pipeline BIS validado son transferibles a Piñero (propiedades sistémicas
3GPP/ENACOM) y cuáles requieren ajuste por entorno local (clutter peri-Rosario vs entorno semi-rural).

### F2 — OpenCellID + Mitsuba
- Query OpenCellID radio 3 km Piñero → CSV enriquecido.
- Convertir `UP9_unidad_alto_perfil.obj` (Blender v18) → Mitsuba 3 XML.
- Validar carga en Sionna local antes de Colab.

### F3 — Ray-tracing en Colab GPU
- Notebook derivado de `pipeline BIS validado` (DB interna).
- 3 bandas prioritarias × 2 alturas = 6 mapas de cobertura.
- Grid ~300-400k puntos, ~1 h compute T4.

### F4 — Validación cruzada y publicación de incertidumbre
- Aplicar calibración two-slope LOS/NLOS heredada de la DB propia BIS.
- Tabla paralela sitio de referencia BIS ↔ Piñero banda por banda.
- Rango de incertidumbre ampliado defendido con referencias académicas.

### F5 — Anexo de 30 slides estilo sitio de referencia BIS
- Replicar estructura de `DB propia BIS · /06_informe_final/slides/`.
- Terminología **S1** (base medida IDR sitio de referencia BIS) / **S2** (extrapolación Piñero).
- NO usar palabras "sintético" ni "Sionna" visibles al cliente.
- PDF final ~40-60 MB.

---

## 4. Entradas disponibles

| Activo | Origen | Estado |
|---|---|---|
| Modelo 3D Blender v18 | `../unidad_v18.blend` | ✅ |
| Export OBJ+MTL+GLB | `../exports_rf/UP9_unidad_alto_perfil.*` | ✅ |
| Manifest RF ITU-R P.2040 | `../exports_rf/UP9_RF_manifest.json` | ✅ |
| CSV 2725 objetos clasificados | `../exports_rf/UP9_objects_rf.csv` | ✅ |
| Plan previo Sionna | `../exports_rf/sionna_plan/PLAN_SIMULACION_RF.md` | ✅ (referencia) |
| Planos PDF complejo Piñero | `../../01_fuentes/planos/*.pdf` (7 archivos) | ✅ |
| Calibración IDR sitio de referencia BIS | `DB propia BIS · /03_sintetico/*.py` + `05_analisis_rf/REPORTE_FASE5_ANALISIS.md` | ✅ |

---

## 5. Nota de naming

Los archivos en `../exports_rf/` tienen prefijo `UP9_` heredado del pipeline de template interno,
pero son geometría de **UP N°8 Piñero**. Para evitar confusión:
- Archivos fuente → se mantienen con prefijo `UP9_*` (no renombrar para no romper referencias).
- Archivos producidos acá (outputs F2-F5) → prefijo `PINERO_UP8_*`.
- Documentación → siempre explicita "UP N°8 Piñero" para el cliente.

---

## 6. Referencias cruzadas

| Consume | Usado en |
|---|---|
| Este anexo | `08_Pliego_PROPUESTA_BIS_MOTOROLA/BIS_MOTOROLA_Sistema_Inhibicion_Pinero_V1_1.docx` (referenciado como "Anexo Técnico RF del Mini Penal A") |
| Este anexo | `09_Propuesta_Final_Motorola/slides/*.html` (referenciado como "Anexo Técnico" en deck comercial) |
| pipeline BIS validado | Fuente de calibración, metodología y estilo visual |

---

**Arranque**: 2026-04-24
**Responsable**: Maximiliano Keczeli (BIS)
**Cliente**: Motorola Solutions Argentina — CP 01/26 Santa Fe
