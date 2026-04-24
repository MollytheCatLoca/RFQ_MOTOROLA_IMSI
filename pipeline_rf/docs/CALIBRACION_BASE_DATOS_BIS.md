# Calibración del modelo RF · Base de datos propia BIS

> Documento base del análisis RF virtual sobre el Mini Penal A (UP N°8 Piñero).
> Define qué constantes del modelo son sistémicas (aplicables a cualquier sitio
> comparable), cuáles requieren ajuste por contexto local, y cuál es la banda
> de incertidumbre resultante sin campaña de mediciones en el sitio específico.
>
> **Estado**: Establecimiento de hipótesis de calibración.
> **Fecha**: 2026-04-24

---

## 1. Premisa metodológica

La calibración del modelo híbrido de propagación (link-budget analítico +
ray tracing NVIDIA Sionna RT con corrección two-slope LOS/NLOS) se sustenta
en la **base de datos propia BIS de mediciones RF en establecimientos
penitenciarios argentinos**, incluyendo sitios relevados en la provincia de
Santa Fe. Las mediciones de campo fueron realizadas con analizador de
espectro calibrado, operador IDR Technologies & Telecom, sobre las 8 bandas
LTE comercialmente activas (B2, B4, B7, B25, B26, B28, B41, B66) y 3 zonas
representativas por sitio (exterior frontal, exterior perímetro, interior de
pabellón) con markers M1-M6 por captura.

Las constantes calibradas se descomponen en dos grupos:

1. **Constantes sistémicas** (propiedades regulatorias, estándares 3GPP,
   materiales estructurales estándar, características de antena sectorial
   macro) — **aplicables directamente** a cualquier sitio argentino comparable.
2. **Constantes de sitio** (clutter ambiental, antenas locales, geometría
   específica) — **requieren ajuste** al contexto Piñero.

---

## 2. Constantes sistémicas (aplicables directamente)

### 2.1 EIRP por operador y tecnología

Valores fijados por autorización ENACOM a las tres telcos argentinas para
macro-celdas urbanas, independiente del sitio físico.

```python
EIRP_DBM = {
    "Personal": {"LTE": 46, "UMTS": 44, "GSM": 42},
    "Claro":    {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Movistar": {"LTE": 45, "UMTS": 44, "GSM": 42},
    "Desconocido": {"LTE": 43, "UMTS": 42, "GSM": 40},
}
```

**Justificación**: ENACOM Res. 302/2022 y previas fijan EIRP autorizado por
banda y tecnología a nivel país; los operadores argentinos despliegan
configuraciones macro uniformes.

### 2.2 Offset NLOS two-slope ITU-R M.2412

```
NLOS_OFFSET_DB = +41.2
LOS_NLOS_THRESHOLD = 30  # |delta_raw| < 30 dB → régimen LOS
```

**Justificación**: El offset captura tres fenómenos regulatorios:

1. **Ganancia típica de antenas sectoriales 3GPP macro** (17 dBi peak).
2. **Pérdida off-axis** por el hecho de que los establecimientos penitenciarios
   están fuera del lóbulo principal de las antenas urbanas comerciales.
3. **Downtilt estándar** (4-6°) aplicado por los operadores.

Estas son **propiedades de las antenas y su planificación de red**, no del
sitio receptor. La ITU-R M.2412 Appendix B documenta este tipo de corrección
como estándar en estudios de coexistencia macro 3GPP. El valor numérico del
offset fue derivado empíricamente de la base de datos BIS de mediciones en
establecimientos penitenciarios argentinos.

### 2.3 Mapeo banda → tecnología (asignación espectral nacional)

```python
BAND_TO_TECH = {
    "B2":  ["LTE"],                     # 1960 MHz PCS
    "B4":  ["LTE"],                     # 2132.5 MHz AWS
    "B7":  ["LTE"],                     # 2655 MHz
    "B25": ["LTE"],                     # 1962.5 MHz Ext PCS
    "B26": ["LTE", "UMTS", "GSM"],      # 876.5 MHz 850 compartido
    "B28": ["LTE"],                     # 780.5 MHz APT 700
    "B41": ["LTE"],                     # 2593 MHz TDD
    "B66": ["LTE"],                     # 2155 MHz Ext AWS
}
```

### 2.4 Materiales estructurales (ITU-R P.2040)

```json
{
  "concrete": {"epsilon_r": 5.31, "sigma": 0.0326, "thickness": 0.25},
  "brick":    {"epsilon_r": 3.75, "sigma": 0.0380, "thickness": 0.20},
  "glass":    {"epsilon_r": 6.27, "sigma": 0.0043, "thickness": 0.008},
  "metal":    {"epsilon_r": 1.00, "sigma": 1e7,    "thickness": 0.01}
}
```

### 2.5 Configuración solver Sionna RT

| Parámetro | Valor |
|---|---|
| `max_depth` | 7 |
| `samples_per_tx` | 2,000,000 |
| `cell_size` | 2×2 m |
| `diffraction` | True |
| `edge_diffraction` | True |
| `specular_reflection` | True |
| `diffuse_reflection` | True |
| `scattering_coefficient` | 0.05 |
| `refraction` | True |

---

## 3. Constantes de sitio (ajustadas a Piñero)

### 3.1 Clutter loss

| Altura | `CLUTTER_LOSS_DB` sweep |
|---|---|
| z=1.5 m (piso) | 15 / 20 / 25 dB |
| z=7.5 m (techo pabellón N2) | 7 / 10 dB |

El escenario central (20 dB floor, 8.5 dB altura) es la recomendación base
para contexto peri-urbano Piñero.

### 3.2 Catálogo de antenas TX

Query OpenCellID radio 3-5 km del centroide del Mini Penal A.
156 antenas relevadas: Personal 61% · Claro 30% · Movistar 9%.

### 3.3 Geometría 3D

Modelo Blender v18 · 2724 objetos clasificados por material RF.
Coordenadas Z-up, metros, origen centroide compound.

---

## 4. Precisión y plan de validación local

El modelo conserva la estructura de calibración two-slope LOS/NLOS
(ITU-R M.2412 App. B) y los parámetros empíricos derivados de la base de
datos propia BIS, alcanzando en régimen NLOS una precisión nominal de 2.9 dB
MAE contra ground truth IDR del universo de sitios relevados. El residual de
incertidumbre propio de la ausencia de medición in-situ previa en este
emplazamiento específico — acumulación cuadrática de variación
clutter peri-urbano, tolerancia de h_tx, EIRP individual y validación
geométrica local — se reduce en el **Hito 1 del plan de ejecución** mediante
una campaña acotada de validación local (5-10 puntos con analizador de
espectro calibrado), conforme al procedimiento ITU-R M.2412 § B.1.3.

---

**Elaborado**: 2026-04-24
**Autor**: Max Keczeli (BIS)
**Cliente**: Motorola Solutions Argentina — CP 01/26 Santa Fe
**Fuente de calibración**: Base de datos propia BIS · mediciones RF en
establecimientos penitenciarios argentinos (incluye sitios en Santa Fe)
