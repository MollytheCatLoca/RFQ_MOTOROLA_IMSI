#!/usr/bin/env python3
"""
Enriquecimiento del dataset de antenas celulares en la zona del Mini Penal A
(UP N°8 Piñero, Santa Fe).

Input:  antenas_pinero_raw.csv   (156 antenas desde OpenCellID, scraping DIC-2025)
Output: antenas_pinero_enriched.csv  (mismo set + distancia/bearing al centroide
        UP8 Piñero + operador derivado de MNC + bandas LTE estimadas)

Adaptado del enricher original de Recreo:
  RFQ_Recreo/04_ejecucion/auxiliares/analisis_espectro_rf/01_parsing/enrich_antenas.py

Diferencias respecto a Recreo:
- Centroide UP8 Piñero: -33.0927, -60.8005 (del mapa interactivo ANTENAS_DB DIC-2025)
- Dataset más chico (156 antenas vs 398 de Recreo) porque el scraping original tenía
  radio menor en el query de Piñero. Para F3 esto puede requerir ampliar el query si
  queremos cobertura de las 3 telcos hasta 5 km.

Uso:
    python3 enrich_antenas_pinero.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).parent

# ============================================================================
# Centroide UP N°8 Piñero (Complejo Penitenciario - Mini Penal A)
# Fuente: mapa interactivo ANTENAS_DB DIC-2025 setView center
#   RFQs_Motorola_DIC25/ANTENAS_DB/data/exports/mapa_interactivo_pinero.html
# Nota: validar contra Google Earth si hace falta precisión <100m
# ============================================================================
UP8_LAT = -33.09270383406942
UP8_LON = -60.80047176165265

# MNC → operador (Argentina, MCC 722) — heredado del enricher Recreo
OPERATORS = {
    7:   "Movistar",       # Telefónica Móviles Argentina
    10:  "Personal (old)", # Telecom Personal (MNC histórico)
    34:  "Personal",       # Telecom Personal (MNC actual)
    40:  "Nextel",         # Integrado en Personal desde 2017
    310: "Claro",          # AMX Argentina
    320: "Claro",          # AMX Argentina (MNC alternativo)
    399: "Desconocido",    # Probable operador transitorio / MVNO
}

TECH_TO_BANDS = {
    ("GSM",  "Movistar"): ["B5 (850)", "B2 (1900)"],
    ("GSM",  "Personal"): ["B5 (850)", "B2 (1900)"],
    ("GSM",  "Claro"):    ["B5 (850)", "B2 (1900)"],
    ("UMTS", "Movistar"): ["B5 (850)", "B1 (2100)"],
    ("UMTS", "Personal"): ["B5 (850)", "B1 (2100)"],
    ("UMTS", "Claro"):    ["B5 (850)", "B1 (2100)"],
    ("LTE",  "Movistar"): ["B28 (700)", "B4 (AWS)", "B7 (2600)"],
    ("LTE",  "Personal"): ["B28 (700)", "B4 (AWS)", "B7 (2600)"],
    ("LTE",  "Claro"):    ["B28 (700)", "B4 (AWS)", "B7 (2600)"],
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def operator_of(mnc: int) -> str:
    return OPERATORS.get(mnc, f"MNC-{mnc}")


def bands_of(radio: str, operator: str) -> list[str]:
    op_key = (
        "Movistar" if operator == "Movistar"
        else ("Personal" if "Personal" in operator else
              "Claro" if operator == "Claro" else operator)
    )
    return TECH_TO_BANDS.get((radio, op_key), ["unknown"])


def main():
    src = HERE / "antenas_pinero_raw.csv"
    dst = HERE / "antenas_pinero_enriched.csv"
    summary = HERE / "antenas_pinero_summary.json"

    assert src.exists(), f"Falta input {src}"

    rows_out = []
    stats = {
        "total": 0,
        "centroid_up8": {"lat": UP8_LAT, "lon": UP8_LON},
        "by_operator": {},
        "by_radio": {},
        "by_distance_bucket_km": {"0-1": 0, "1-3": 0, "3-5": 0, "5-10": 0, "10+": 0},
        "nearest": None,
        "antennas_in_2km": 0,
        "antennas_in_3km": 0,
        "antennas_in_5km": 0,
    }

    with src.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = float(row["lat"])
            lon = float(row["lon"])
            mnc = int(row["mnc"])
            radio = row["radio"].strip()
            operator = operator_of(mnc)
            dist = haversine_km(UP8_LAT, UP8_LON, lat, lon)
            brg = bearing_deg(UP8_LAT, UP8_LON, lat, lon)
            bands = bands_of(radio, operator)

            stats["total"] += 1
            stats["by_operator"][operator] = stats["by_operator"].get(operator, 0) + 1
            stats["by_radio"][radio] = stats["by_radio"].get(radio, 0) + 1
            if dist <= 1:
                stats["by_distance_bucket_km"]["0-1"] += 1
            elif dist <= 3:
                stats["by_distance_bucket_km"]["1-3"] += 1
            elif dist <= 5:
                stats["by_distance_bucket_km"]["3-5"] += 1
            elif dist <= 10:
                stats["by_distance_bucket_km"]["5-10"] += 1
            else:
                stats["by_distance_bucket_km"]["10+"] += 1
            if dist <= 2:
                stats["antennas_in_2km"] += 1
            if dist <= 3:
                stats["antennas_in_3km"] += 1
            if dist <= 5:
                stats["antennas_in_5km"] += 1
            if stats["nearest"] is None or dist < stats["nearest"]["distance_km"]:
                stats["nearest"] = {
                    "id": int(row["id"]),
                    "operator": operator,
                    "radio": radio,
                    "lat": lat, "lon": lon,
                    "distance_km": round(dist, 3),
                    "bearing_deg": round(brg, 1),
                    "cellid": row["cellid"],
                }

            rows_out.append({
                **row,
                "operator": operator,
                "distance_km_to_up8": round(dist, 3),
                "bearing_deg_from_up8": round(brg, 1),
                "estimated_bands": "; ".join(bands),
            })

    rows_out.sort(key=lambda r: r["distance_km_to_up8"])

    fieldnames = list(rows_out[0].keys())
    with dst.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    with summary.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"✅ Procesadas {stats['total']} antenas")
    print(f"   Centroide UP8: {UP8_LAT:.5f}, {UP8_LON:.5f}")
    print(f"   Output: {dst.name}")
    print(f"   Summary: {summary.name}")
    print()
    print("Por operador:")
    for op, n in sorted(stats["by_operator"].items(), key=lambda x: -x[1]):
        print(f"   {op:20s} {n:4d}  ({100*n/stats['total']:.1f}%)")
    print()
    print("Por tecnología:")
    for r, n in sorted(stats["by_radio"].items(), key=lambda x: -x[1]):
        print(f"   {r:10s} {n:4d}  ({100*n/stats['total']:.1f}%)")
    print()
    print("Por distancia a UP8 Piñero:")
    for bucket, n in stats["by_distance_bucket_km"].items():
        print(f"   {bucket:6s} km  {n:4d}  ({100*n/stats['total']:.1f}%)")
    print()
    print(f"Antenas dentro de 2 km: {stats['antennas_in_2km']}")
    print(f"Antenas dentro de 3 km: {stats['antennas_in_3km']}")
    print(f"Antenas dentro de 5 km: {stats['antennas_in_5km']}")
    print()
    print(f"Antena más cercana: {stats['nearest']}")


if __name__ == "__main__":
    main()
