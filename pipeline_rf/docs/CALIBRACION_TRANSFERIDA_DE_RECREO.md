# F1 · Calibración transferida de Recreo a Piñero

> Documento base del análisis RF virtual sobre el Mini Penal A (UP N°8 Piñero).
> Define qué constantes del pipeline Recreo son transferibles, cuáles requieren
> ajuste, y cuál es la banda de incertidumbre que resulta sin mediciones locales.
>
> **Estado**: Fase 1 — Establecimiento de hipótesis de transferencia.
> **Fecha**: 2026-04-24
> **Fuentes**: scripts `03_sintetico/build_sintetico_{floor,altura}.py` y reporte
> `05_analisis_rf/REPORTE_FASE5_ANALISIS.md` del pipeline Recreo.

---

## 1. Premisa

El pipeline de Recreo calibró un modelo híbrido (link-budget analítico + ray tracing Sionna con
two-slope LOS/NLOS) contra **22 mediciones reales IDR** en 3 puntos de referencia (MS1/MS2/MS3)
sobre 8 bandas LTE, alcanzando **MAE 2,90 dB en régimen NLOS** y MAE 6,59 dB global.

Piñero no tiene campaña de campo disponible. La hipótesis de trabajo es que las constantes
calibradas en Recreo se descomponen en dos grupos:

1. **Constantes sistémicas** (propiedades regulatorias, estándares 3GPP, materiales
   estructurales estándar, características de antena sectorial macro) — **transferibles
   directamente** a cualquier sitio argentino comparable.
2. **Constantes de sitio** (clutter ambiental, altura de antenas TX locales, geometría
   específica) — **requieren ajuste** al contexto Piñero.

El documento separa ambos grupos y justifica cada decisión.

---

## 2. Constantes transferibles directamente (propiedades sistémicas)

### 2.1 EIRP por operador y tecnología

Los valores están fijados por la autorización ENACOM a las tres telcos argentinas para
macro-celdas urbanas, independiente del sitio físico. Se heredan 1:1.

```python
EIRP_DBM = {
    "Personal": {"LTE": 46, "UMTS": 44, "GSM": 42},
    "Claro":    {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Movistar": {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Desconocido": {"LTE": 43, "UMTS": 42, "GSM": 40},
}
```

**Por qué transfiere**: ENACOM Res. 302/2022 y previas fijan EIRP autorizado por banda y
tecnología a nivel país; los operadores argentinos desplegan configuraciones macro
uniformes (misma cartera de equipos Huawei/Ericsson/Nokia).

### 2.2 Offset NLOS two-slope ITU-R M.2412

```
NLOS_OFFSET_DB = +41.2
LOS_NLOS_THRESHOLD = 30  # |delta_raw| < 30 dB → régimen LOS
```

**Por qué transfiere**: El offset empírico de Recreo captura tres fenómenos regulatorios:
1. **Ganancia típica de antenas sectoriales 3GPP macro** (17 dBi peak).
2. **Pérdida off-axis** por el hecho de que el penal está fuera del lóbulo principal de las
   antenas urbanas (diseñadas para cubrir núcleo poblado).
3. **Downtilt estándar** (4-6°) aplicado por los operadores para reducir interferencia inter-celda.

Estas son **propiedades de las antenas y su planificación de red**, no del sitio receptor.
La ITU-R M.2412 Appendix B documenta este tipo de corrección como estándar en estudios de
coexistencia macro 3GPP.

### 2.3 Mapeo banda → tecnología (asignación espectral nacional)

```python
BAND_TO_TECH = {
    "B2":  ["LTE"],                     # 1960 MHz PCS
    "B4":  ["LTE"],                     # 2132.5 MHz AWS
    "B7":  ["LTE"],                     # 2655 MHz
    "B25": ["LTE"],                     # 1962.5 MHz Ext PCS
    "B26": ["LTE", "UMTS", "GSM"],      # 876.5 MHz 850 espectro compartido
    "B28": ["LTE"],                     # 780.5 MHz APT 700
    "B41": ["LTE"],                     # 2593 MHz TDD
    "B66": ["LTE"],                     # 2155 MHz Ext AWS
}
```

**Por qué transfiere**: asignaciones ENACOM nacionales. Las mismas telcos usan las mismas
bandas en todo el país.

### 2.4 Materiales estructurales (ITU-R P.2040)

Del manifest `UP9_RF_manifest.json` (que ya existe en Piñero):

```json
{
  "concrete": {"epsilon_r": 5.31, "sigma": 0.0326, "thickness": 0.25},
  "brick":    {"epsilon_r": 3.75, "sigma": 0.0380, "thickness": 0.20},
  "glass":    {"epsilon_r": 6.27, "sigma": 0.0043, "thickness": 0.008},
  "metal":    {"epsilon_r": 1.00, "sigma": 1e7,    "thickness": 0.01}
}
```

**Por qué transfiere**: el hormigón armado argentino cumple norma IRAM similar a
estándares internacionales; las propiedades dieléctricas relevadas por ITU-R P.2040-3 son
globales. Recreo y Piñero usan hormigón estructural comparable (confirmado en ambos planos).

### 2.5 Altura típica antenas TX macro (h_tx)

```
H_TX_ASSUMED_M = 25.0
```

**Por qué transfiere**: es la altura promedio de macro-celdas urbanas/suburbanas en Argentina
(torres autosoportadas 20-35 m). Validable al cruzar OpenCellID Piñero.

### 2.6 Calibración two-slope LOS/NLOS (Sionna RT 2.0.1)

| Parámetro solver | Valor | Transferibilidad |
|---|---|---|
| `max_depth` | 5 | ✅ (regla de rebotes 3GPP) |
| `samples_per_tx` | 1,000,000 | ✅ (balance precisión/tiempo) |
| `cell_size` | 2×2 m | ✅ (operativo para IMSI/jammer) |
| `diffraction` | True | ✅ |
| `edge_diffraction` | True | ✅ |
| `specular_reflection` | True | ✅ |
| `diffuse_reflection` | False | ✅ (evita sobreestimación) |
| `refraction` | True | ✅ |

Estos son parámetros numéricos del solver, no dependen del sitio.

---

## 3. Constantes de sitio (requieren ajuste Piñero)

### 3.1 Clutter loss a nivel suelo (z=1.5 m) — **AJUSTE CRÍTICO**

| Sitio | Entorno | `CLUTTER_LOSS_DB` propuesto | Justificación |
|---|---|---|---|
| **Recreo** (calibrado) | Semi-rural · vegetación extensa · aislado 7 km del núcleo urbano Santa Fe | **25 dB** | Okumura-Hata suburbano + arboledas |
| **Piñero** (propuesta) | Peri-urbano Rosario · vegetación baja · 3-4 km zona industrial | **15-20 dB** | Menos shadowing vegetal pero más edificación circundante |

**Metodología propuesta**: sweep de sensibilidad en tres escenarios (15 / 20 / 25 dB) y
publicar la terna completa en F4. El escenario central (20 dB) es la recomendación base;
los extremos muestran robustez del análisis.

**Justificación peri-urbano Piñero**:
- Piñero está a 17 km al SO del centro de Rosario, sobre corredor industrial RN A008.
- Entorno inmediato: zona rural/industrial con vegetación baja, vs Recreo que tiene arboledas
  maduras.
- La densidad edilicia del complejo (4 mini penales + planta gobierno + pabellones) es
  mayor a Recreo, pero las mediciones serían en punto interior (similar).

### 3.2 Clutter loss en altura (z=7.5 m)

| Sitio | `CLUTTER_LOSS_DB @ z=7.5m` |
|---|---|
| Recreo (calibrado) | **10 dB** (reducción por LoS sobre arboleda) |
| Piñero (propuesta) | **7-10 dB** (LoS más clara por ausencia de arboleda alta) |

Se hereda el valor de Recreo (10 dB) como límite superior conservador. Sensibilidad a 7 dB
se reporta en F4 como cota inferior.

### 3.3 Antena mispointing

```
ANTENNA_MISPOINTING_DB = 5.0
```

**Ajuste Piñero**: **se hereda** (5 dB). Aunque técnicamente es una propiedad del sitio
(hacia dónde apuntan las antenas urbanas vecinas), el valor es compatible con cualquier
penal argentino típicamente ubicado en periferia del núcleo poblado.

### 3.4 Catálogo de antenas TX

Piñero requiere **re-query OpenCellID** radio 3 km del centroide del Mini Penal A. Es dato
de sitio puro, no transferible.

Coordenadas centroide Mini Penal A (de `UP9_RF_manifest.json`): **pendiente extracción en F2**.

### 3.5 Geometría 3D del sitio

Ya disponible (modelo Blender v18, 2724 objetos). **Más detallada que Recreo** (Recreo usó
20 edificios extruidos simples). Esta es una **ventaja** de Piñero, no una desventaja — la
fidelidad geométrica es superior.

---

## 4. Tabla resumen de transferencia

| Constante | Valor Recreo | Valor Piñero | Tipo |
|---|:---:|:---:|---|
| EIRP Personal LTE | 46 dBm | 46 dBm | 🟢 Transferible |
| EIRP Claro/Movistar LTE | 45 dBm | 45 dBm | 🟢 Transferible |
| EIRP GSM (todos) | 42 dBm | 42 dBm | 🟢 Transferible |
| NLOS offset two-slope | +41.2 dB | +41.2 dB | 🟢 Transferible |
| LOS/NLOS threshold | 30 dB | 30 dB | 🟢 Transferible |
| BAND_TO_TECH | ver tabla | idem | 🟢 Transferible |
| Material concrete εr | 5.31 | 5.31 | 🟢 Transferible |
| Material concrete σ | 0.0326 S/m | 0.0326 S/m | 🟢 Transferible |
| h_tx asumida | 25 m | 25 m | 🟢 Transferible (validable) |
| `max_depth` solver | 5 | 5 | 🟢 Transferible |
| `cell_size` | 2×2 m | 2×2 m | 🟢 Transferible |
| Antena mispointing | 5 dB | 5 dB | 🟢 Transferible |
| **CLUTTER_LOSS @ z=1.5** | **25 dB** | **15 / 20 / 25 dB (sweep)** | 🟡 Sitio — ajustar |
| **CLUTTER_LOSS @ z=7.5** | **10 dB** | **7 / 10 dB (sweep)** | 🟡 Sitio — ajustar |
| **muro_db** por objeto | 25 dB (pabellón hormigón) | Por CSV 2725 obj (más fino) | 🟡 Sitio — más detallado |
| Catálogo antenas TX | 398 OpenCellID Recreo | Re-query Piñero | 🟡 Sitio — re-levantar |
| Polígono perímetro | UP9_CORNERS | Extraer de manifest v18 | 🟡 Sitio — re-derivar |

---

## 5. Banda de incertidumbre esperada

### 5.1 MAE alcanzado en Recreo

| Modelo | MAE (dB) |
|---|:---:|
| Analítico solo (Fase 3A) | 9.30 |
| Sionna raw (sin calibración) | 31.41 |
| **Sionna calibrado two-slope** | **6.59 global** |
| Sionna calibrado · régimen NLOS | **2.90** |
| Sionna calibrado · régimen LOS | 12.73 |

### 5.2 MAE esperado en Piñero (sin mediciones locales)

Al transferir la calibración sin validación local, se acumulan tres fuentes adicionales de
incertidumbre:

| Fuente | Contribución estimada |
|---|---|
| Variación clutter peri-urbano (sweep 15-25 dB) | ±3-5 dB |
| Error de h_tx real antenas Piñero vs asumida 25 m (±5 m) | ±0.5 dB FSPL |
| Desconocimiento EIRP real por celda (suponemos valor típico) | ±3 dB |
| Geometría local no validada contra medición | ±2 dB |
| **Total acumulado en cuadratura** | **±5.0 dB** |

**MAE NLOS proyectado Piñero**: **6 - 8 dB** (vs 2.90 dB de Recreo)
**MAE global proyectado Piñero**: **9 - 11 dB** (vs 6.59 dB de Recreo)

### 5.3 Cómo se reporta al cliente

El anexo F5 incluye una slide dedicada (estilo slide 23-24 de Recreo) que:
1. Publica MAE de Recreo validado como evidencia de la metodología.
2. Documenta abiertamente que Piñero usa calibración transferida.
3. Reporta banda de incertidumbre ampliada (+3-5 dB).
4. Propone **campaña de validación local como parte del plan de verificación post-adjudicación**
   (5-10 puntos de medición con analizador de espectro en sitio).

Esto convierte una limitación en una propuesta de valor: validación de la simulación contra
mediciones locales como parte de E5 (soporte QA) o como extensión del alcance de instalación.

---

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Clutter Piñero fuera del sweep 15-25 dB | Ampliar sweep a 10-30 dB si resultados parecen inconsistentes con literatura |
| Material hormigón Piñero distinto al usado en Recreo | CSV de 2725 objetos Piñero es más detallado — usa materiales por-objeto |
| Antenas OpenCellID desactualizadas | Validar al menos 3-5 antenas contra consulta directa ENACOM/operadores |
| MAE proyectado > 10 dB en sweep final | Reporte honesto en slide de validación; recomendación de campaña medición local |
| Cliente cuestiona transferencia desde Recreo | Slide dedicada explica propiedades sistémicas vs sitio; referencias ITU-R M.2412 + Degli-Esposti 2019 |

---

## 7. Outputs F1

| Archivo | Estado |
|---|---|
| `CALIBRACION_TRANSFERIDA_DE_RECREO.md` (este documento) | ✅ |
| `parametros_calibrados.py` (módulo Python reutilizable por F2/F3) | ⏳ siguiente paso |
| `justificacion_transferencia.md` (bibliografía y referencias) | ⏳ siguiente paso |

---

## 8. Próximo paso

Generar `parametros_calibrados.py` con las constantes en forma de módulo importable por los
scripts de F3 (análogo a cómo `build_sintetico_floor.py` de Recreo tiene sus constantes
embebidas). Esto cierra F1 y habilita F2.

---

**Elaborado**: 2026-04-24
**Autor**: Max Keczeli (BIS) · Análisis RF Virtual Piñero
**Cliente**: Motorola Solutions Argentina — CP 01/26 Santa Fe
**Fuente de calibración**: Pipeline Recreo (`RFQ_Recreo/04_ejecucion/auxiliares/analisis_espectro_rf/`)
