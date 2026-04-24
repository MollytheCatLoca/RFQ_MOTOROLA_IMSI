#!/usr/bin/env python3
"""
Converter OBJ + manifest RF → Mitsuba 3 XML para Sionna RT 2.x

Genera:
  1. PINERO_UP8_scene.xml      — escena Mitsuba con BSDFs visuales + todos los OBJ
                                   importados como un único shape (Sionna asigna radio
                                   materials por-objeto después).
  2. material_mapping.json      — diccionario object_name → rf_material consumido por
                                   el notebook Colab (evita hardcoding en el notebook).
  3. scene_stats.json           — métricas de la conversión (N objetos por material,
                                   bounding box global, centroide).

Notas de diseño:
  - Sionna RT no necesita que cada objeto esté separado físicamente; el matching se
    hace vía nombre en Python con `scene.get(name).radio_material = "itu_concrete"`.
  - El XML Mitsuba se genera con BSDFs ficticios (sólo para preview visual); los
    radio materials se sobrescriben en el notebook vía el manifest ITU-R P.2040-3.
  - El OBJ no se transforma; se referencia relativo al XML.

Uso:
    python3 obj_to_mitsuba.py

Inputs esperados:
    ../exports_rf/UP9_unidad_alto_perfil.obj   (66,140 líneas · 2724 objetos)
    ../exports_rf/UP9_unidad_alto_perfil.mtl   (16 materiales visuales)
    ../exports_rf/UP9_RF_manifest.json         (bbox + rf_material por objeto)
    ../exports_rf/UP9_objects_rf.csv           (lookup csv)
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).parent
EXPORTS_RF = HERE.parent.parent / "exports_rf"

IN_OBJ = EXPORTS_RF / "UP9_unidad_alto_perfil.obj"
IN_MTL = EXPORTS_RF / "UP9_unidad_alto_perfil.mtl"
IN_MANIFEST = EXPORTS_RF / "UP9_RF_manifest.json"
IN_CSV = EXPORTS_RF / "UP9_objects_rf.csv"

OUT_XML = HERE / "PINERO_UP8_scene.xml"
OUT_MAPPING = HERE / "material_mapping.json"
OUT_STATS = HERE / "scene_stats.json"


def load_manifest() -> dict:
    with IN_MANIFEST.open() as f:
        return json.load(f)


def load_csv_mapping() -> Dict[str, dict]:
    """Devuelve dict object_name → {rf_material, epsilon_r, sigma, thickness}."""
    mapping = {}
    with IN_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["object_name"]] = {
                "rf_material": row["rf_material"],
                "epsilon_r": float(row["epsilon_r"]),
                "sigma_S_m": float(row["sigma_S_m"]),
                "thickness_m": float(row["thickness_m"]),
            }
    return mapping


def parse_obj_bbox(obj_path: Path) -> Tuple[List[float], List[float]]:
    """Extrae bbox global (xmin,ymin,zmin), (xmax,ymax,zmax) del OBJ."""
    xmin, ymin, zmin = math.inf, math.inf, math.inf
    xmax, ymax, zmax = -math.inf, -math.inf, -math.inf
    with obj_path.open() as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                xmin, ymin, zmin = min(xmin, x), min(ymin, y), min(zmin, z)
                xmax, ymax, zmax = max(xmax, x), max(ymax, y), max(zmax, z)
    return [xmin, ymin, zmin], [xmax, ymax, zmax]


# ============================================================================
# Generación XML Mitsuba
# ============================================================================

# BSDFs visuales simples para preview Mitsuba (Sionna sobrescribe con radio materials).
# Colores tomados del rf_materials.color_hex del manifest.
VISUAL_BSDF_TEMPLATE = """    <bsdf type="diffuse" id="bsdf_{rf_material}">
        <rgb name="reflectance" value="{rgb}"/>
    </bsdf>"""

# RGB hex → RGB 0..1 normalized
RF_MATERIAL_COLORS = {
    "concrete":   "0.624 0.604 0.557",   # #9F9A8E
    "brick":      "0.667 0.478 0.353",   # #AA7A5A
    "glass":      "0.302 0.420 0.522",   # #4D6B85
    "metal":      "0.702 0.702 0.725",   # neutral
    "ground_wet": "0.361 0.318 0.235",   # suelo húmedo
    "ground_dry": "0.686 0.600 0.439",   # suelo seco
    "wood":       "0.545 0.365 0.203",   # madera
    "default":    "0.500 0.500 0.500",
}

SCENE_XML_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<!--
  Escena Mitsuba 3 · Mini Penal A · UP N°8 Piñero
  Generada por obj_to_mitsuba.py · 2026-04-24

  Uso en Sionna RT 2.x:
      import sionna.rt as rt
      scene = rt.load_scene("PINERO_UP8_scene.xml")
      # Luego sobrescribir radio materials vía material_mapping.json

  Dimensiones escena: {dim_x:.1f} x {dim_y:.1f} x {dim_z:.1f} m
  Centroide local: ({cx:.2f}, {cy:.2f}, {cz:.2f})
  N objetos fuente: {n_objects} (distribución ver scene_stats.json)
-->
<scene version="2.1.0">

    <!-- Integrador por defecto para preview visual (no usado por Sionna RT) -->
    <default name="spp" value="64"/>
    <integrator type="path">
        <integer name="max_depth" value="3"/>
    </integrator>

    <!-- Cámara preview (orbital sobre centroide) -->
    <sensor type="perspective">
        <string name="fov_axis" value="smaller"/>
        <float name="fov" value="45"/>
        <transform name="to_world">
            <lookat origin="{cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f}"
                    target="{cx:.1f}, {cy:.1f}, {cz:.1f}"
                    up="0, 0, 1"/>
        </transform>
        <sampler type="independent">
            <integer name="sample_count" value="64"/>
        </sampler>
        <film type="hdrfilm">
            <integer name="width" value="1280"/>
            <integer name="height" value="720"/>
            <string name="pixel_format" value="rgb"/>
        </film>
    </sensor>

    <!-- Iluminación ambiental simple (solo para preview) -->
    <emitter type="constant">
        <rgb name="radiance" value="1.0 1.0 1.0"/>
    </emitter>

    <!-- BSDFs visuales (Sionna sobrescribirá con radio materials ITU-R P.2040-3) -->
{bsdfs}

    <!-- Shape principal: importa el OBJ completo (2724 sub-objetos) -->
    <shape type="obj" id="mini_penal_A_pinero">
        <string name="filename" value="{obj_path}"/>
        <ref id="bsdf_{default_material}" name="bsdf"/>
        <boolean name="face_normals" value="true"/>
    </shape>

</scene>
"""


def generate_xml(manifest: dict, mapping: Dict[str, dict],
                 bbox_min: List[float], bbox_max: List[float]) -> str:
    """Arma el XML a partir de los datos cargados."""
    materials_present = set(entry["rf_material"] for entry in mapping.values())
    bsdfs = []
    for mat in sorted(materials_present):
        rgb = RF_MATERIAL_COLORS.get(mat, RF_MATERIAL_COLORS["default"])
        bsdfs.append(VISUAL_BSDF_TEMPLATE.format(rf_material=mat, rgb=rgb))

    cx = (bbox_min[0] + bbox_max[0]) / 2
    cy = (bbox_min[1] + bbox_max[1]) / 2
    cz = (bbox_min[2] + bbox_max[2]) / 2
    dim_x = bbox_max[0] - bbox_min[0]
    dim_y = bbox_max[1] - bbox_min[1]
    dim_z = bbox_max[2] - bbox_min[2]

    # Cámara orbital a distancia ~ max(dim) para buen framing
    cam_dist = max(dim_x, dim_y) * 0.8
    cam_x = cx + cam_dist * 0.8
    cam_y = cy - cam_dist * 1.2
    cam_z = cz + dim_z * 3

    # Default material para el shape (el más frecuente)
    from collections import Counter
    default_material = Counter(entry["rf_material"] for entry in mapping.values()).most_common(1)[0][0]

    # Path relativo del OBJ desde el XML
    obj_path_rel = "../../exports_rf/UP9_unidad_alto_perfil.obj"

    return SCENE_XML_TEMPLATE.format(
        bsdfs="\n".join(bsdfs),
        dim_x=dim_x, dim_y=dim_y, dim_z=dim_z,
        cx=cx, cy=cy, cz=cz,
        cam_x=cam_x, cam_y=cam_y, cam_z=cam_z,
        n_objects=len(mapping),
        obj_path=obj_path_rel,
        default_material=default_material,
    )


def main():
    print(f"Input OBJ:       {IN_OBJ.name}")
    print(f"Input manifest:  {IN_MANIFEST.name}")
    print(f"Input CSV:       {IN_CSV.name}")

    assert IN_OBJ.exists(), f"Falta {IN_OBJ}"
    assert IN_MTL.exists(), f"Falta {IN_MTL}"
    assert IN_MANIFEST.exists(), f"Falta {IN_MANIFEST}"
    assert IN_CSV.exists(), f"Falta {IN_CSV}"

    print()
    print("Cargando manifest RF...")
    manifest = load_manifest()
    print(f"  N materiales definidos: {len(manifest['rf_materials'])}")
    print(f"  N objetos en manifest:  {len(manifest['objects'])}")

    print()
    print("Cargando mapping CSV...")
    mapping = load_csv_mapping()
    print(f"  N objetos en CSV: {len(mapping)}")

    from collections import Counter
    mat_counts = Counter(entry["rf_material"] for entry in mapping.values())
    print(f"  Distribución por material:")
    for mat, n in mat_counts.most_common():
        print(f"    {mat:20s} {n:5d}  ({100*n/len(mapping):.1f}%)")

    print()
    print("Parseando bbox del OBJ (puede tardar ~5-10 s)...")
    bbox_min, bbox_max = parse_obj_bbox(IN_OBJ)
    print(f"  bbox min: ({bbox_min[0]:.2f}, {bbox_min[1]:.2f}, {bbox_min[2]:.2f})")
    print(f"  bbox max: ({bbox_max[0]:.2f}, {bbox_max[1]:.2f}, {bbox_max[2]:.2f})")
    print(f"  dimensiones: "
          f"{bbox_max[0]-bbox_min[0]:.1f} x "
          f"{bbox_max[1]-bbox_min[1]:.1f} x "
          f"{bbox_max[2]-bbox_min[2]:.1f} m")

    print()
    print("Generando XML Mitsuba...")
    xml_content = generate_xml(manifest, mapping, bbox_min, bbox_max)
    OUT_XML.write_text(xml_content)
    print(f"  → {OUT_XML.name}  ({OUT_XML.stat().st_size} bytes)")

    print()
    print("Escribiendo material_mapping.json (consumido por notebook Sionna)...")
    # Formato compacto: object_name → rf_material (el notebook hará el lookup completo)
    compact_mapping = {name: entry["rf_material"] for name, entry in mapping.items()}
    OUT_MAPPING.write_text(json.dumps(compact_mapping, indent=None, ensure_ascii=False))
    print(f"  → {OUT_MAPPING.name}  ({len(compact_mapping)} objetos)")

    print()
    print("Escribiendo scene_stats.json...")
    stats = {
        "scene_name": "MiniPenalA_UP8_Pinero",
        "source_obj": str(IN_OBJ.relative_to(EXPORTS_RF.parent)),
        "n_objects_total": len(mapping),
        "n_materials_rf": len(set(compact_mapping.values())),
        "material_distribution": dict(mat_counts),
        "bbox_min_m": bbox_min,
        "bbox_max_m": bbox_max,
        "dimensions_m": {
            "x": bbox_max[0] - bbox_min[0],
            "y": bbox_max[1] - bbox_min[1],
            "z": bbox_max[2] - bbox_min[2],
        },
        "centroid_local_m": [
            (bbox_min[0] + bbox_max[0]) / 2,
            (bbox_min[1] + bbox_max[1]) / 2,
            (bbox_min[2] + bbox_max[2]) / 2,
        ],
        "coordinate_system": "Right-handed, Z-up, meters (centered on compound origin)",
        "sionna_rt_version_target": "2.0.1 (DB propia BIS)",
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"  → {OUT_STATS.name}")

    print()
    print("✅ Conversión completa. Outputs listos para F3 (notebook Colab Sionna).")


if __name__ == "__main__":
    main()
