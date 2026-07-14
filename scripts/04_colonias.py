"""Colonia aproximada por AGEB, capa de presentacion.

El brief pide "colonias aproximadas (traduccion manual en capa de presentacion, con la
advertencia de equivalencia aproximada)". Una AGEB NO es una colonia: sus limites son
estadisticos, no administrativos, y una AGEB puede cruzar varias colonias. Esto se
resuelve por geocodificacion inversa del centroide (Nominatim / OpenStreetMap) y sirve
SOLO para que un humano ubique la zona. No es un dato oficial ni una equivalencia exacta.

Salida: output/top_ageb_con_colonia.csv
"""
import time
import json
import urllib.request
import urllib.parse
import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

gdf = gpd.read_file(OUT / "ageb_solidaridad.geojson")
rank = gdf[~gdf["sin_dato_censal"].astype(bool)].copy()
pdc = rank[rank["localidad"] == "Playa del Carmen"].sort_values("vivpar_ut_pct", ascending=False)

top10 = pdc.head(10).copy()
franja = pdc[(pdc["vivpar_ut_pct"] >= 6) & (pdc["vivpar_ut_pct"] <= 8)].copy()
sel = pd.concat([top10.assign(lista="top10"), franja.assign(lista="franja_6_8")])

# centroide en proyeccion metrica, luego a lat/lon
cent = sel.to_crs(6372).geometry.centroid.to_crs(4326)
sel["lat"] = cent.y.values
sel["lon"] = cent.x.values


def reverse(lat, lon):
    q = urllib.parse.urlencode({
        "lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "format": "jsonv2",
        "zoom": "16", "addressdetails": "1",
    })
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/reverse?{q}",
        headers={"User-Agent": "estudio-ageb-solidaridad/1.0 (investigacion academica)"},
    )
    try:
        a = json.loads(urllib.request.urlopen(req, timeout=25).read()).get("address", {})
    except Exception as e:
        return f"(fallo: {type(e).__name__})"
    for k in ("neighbourhood", "suburb", "quarter", "residential", "city_district", "village"):
        if a.get(k):
            return a[k]
    return "(no resuelto)"


nombres = []
for _, r in sel.iterrows():
    nombres.append(reverse(r["lat"], r["lon"]))
    time.sleep(1.1)  # politica de uso de Nominatim: 1 req/seg
sel["colonia_aprox"] = nombres

cols = ["lista", "cvegeo", "colonia_aprox", "TVIVPAR", "VIVPAR_HAB", "VIVPAR_UT",
        "vivpar_ut_pct", "semaforo_ut", "lat", "lon"]
sel[cols].to_csv(OUT / "top_ageb_con_colonia.csv", index=False)

pd.set_option("display.width", 200)
print("=== TOP 10 AGEB POR USO TEMPORAL, PLAYA DEL CARMEN ===")
print("(colonia aproximada, equivalencia NO exacta: la AGEB es unidad estadistica)\n")
print(sel[sel["lista"] == "top10"][["cvegeo", "colonia_aprox", "TVIVPAR", "VIVPAR_UT", "vivpar_ut_pct"]].to_string(index=False))
print("\n=== FRANJA DE APROXIMACION 6 a 8% ===\n")
print(sel[sel["lista"] == "franja_6_8"][["cvegeo", "colonia_aprox", "TVIVPAR", "VIVPAR_UT", "vivpar_ut_pct"]].to_string(index=False))
