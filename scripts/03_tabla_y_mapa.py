"""Tabla por AGEB y mapa, Solidaridad.

IMPORTANTE, y no es un detalle de forma.

El brief define el indice de penetracion como listings / TVIVPAR. Ese indice NO se
calcula aqui, porque el numerador (listings georreferenciados) no se pudo levantar
en esta corrida. Ver output/NUMERADOR_VIABILIDAD.md.

Lo que si se calcula es el CONTROL que el propio brief ordena en su seccion de
controles obligatorios: VIVPAR_UT / TVIVPAR. El brief dice literalmente que ese
contraste "es producto, no solo control". Se entrega como lo que es, con su nombre,
y en ningun lado se presenta como el indice.

Salidas: output/ageb_solidaridad.csv, output/ageb_solidaridad.geojson, output/mapa.html
"""
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

UMBRAL = 8.0          # umbral de referencia de Malaga. NO es norma local.
FRANJA_INF = 6.0      # franja de aproximacion

den = pd.read_csv(OUT / "denominador_solidaridad.csv", dtype={"cvegeo": str, "LOC": str})
geo = gpd.read_file(ROOT / "data/mg23/conjunto_de_datos/23a.shp")
geo = geo[geo["CVE_MUN"] == "008"][["CVEGEO", "geometry"]].to_crs(4326)

df = geo.merge(den, left_on="CVEGEO", right_on="cvegeo", how="inner")
assert len(df) == len(den), "perdida en el join"

df["localidad"] = df["LOC"].map({"0001": "Playa del Carmen", "0308": "Puerto Aventuras"})

def semaforo(p):
    if pd.isna(p):
        return "sin dato"
    if p > UMBRAL:
        return "rojo"
    if p >= FRANJA_INF:
        return "ambar"
    return "verde"

df["semaforo_ut"] = df["vivpar_ut_pct"].apply(semaforo)

# Columnas que el brief pide y que esta corrida no puede llenar. Se dejan explicitas y vacias.
df["listings_bruta"] = pd.NA
df["listings_ajustada"] = pd.NA
df["penetracion_pct"] = pd.NA          # el indice del brief. Bloqueado por el numerador.
df["asignaciones_ambiguas"] = pd.NA
df["vector_asamblea"] = pd.NA          # placeholder ordenado por el brief

cols = ["cvegeo", "localidad", "POBTOT", "TVIVPAR", "VIVPAR_HAB", "VIVPAR_DES",
        "VIVPAR_UT", "vivpar_ut_pct", "semaforo_ut", "listings_bruta",
        "listings_ajustada", "penetracion_pct", "asignaciones_ambiguas",
        "vector_asamblea", "celdas_reservadas", "sin_dato_censal"]

tab = df[cols].sort_values("vivpar_ut_pct", ascending=False, na_position="last")
tab.to_csv(OUT / "ageb_solidaridad.csv", index=False)
df[cols + ["geometry"]].to_file(OUT / "ageb_solidaridad.geojson", driver="GeoJSON")

rank = tab[~tab["sin_dato_censal"]]
pdc = rank[rank["localidad"] == "Playa del Carmen"]
pav = rank[rank["localidad"] == "Puerto Aventuras"]

print("=" * 72)
print("CONTROL CENSAL VIVPAR_UT / TVIVPAR POR AGEB, SOLIDARIDAD")
print("Esto NO es el indice del brief. Es el control obligatorio.")
print("=" * 72)

for nombre, loc in [("PLAYA DEL CARMEN", "Playa del Carmen"), ("PUERTO AVENTURAS", "Puerto Aventuras")]:
    sub = rank[rank["localidad"] == loc]
    todas = tab[tab["localidad"] == loc]
    fuera = todas[todas["sin_dato_censal"].astype(bool)]
    print(f"\n--- {nombre} ---")
    print(f"AGEB totales: {len(todas)} | rankeables: {len(sub)} | no rankeables: {len(fuera)}")
    print(f"Sobre las rankeables: TVIVPAR {int(sub['TVIVPAR'].sum()):,} | VIVPAR_UT {int(sub['VIVPAR_UT'].sum()):,}")
    print(f"Uso temporal agregado: {sub['VIVPAR_UT'].sum() / sub['TVIVPAR'].sum() * 100:.2f}%")
    print(f"  AGEB sobre el umbral de 8%: {(sub['semaforo_ut'] == 'rojo').sum()}")
    print(f"  AGEB en franja 6 a 8%:      {(sub['semaforo_ut'] == 'ambar').sum()}")
    print(f"  AGEB bajo 6%:               {(sub['semaforo_ut'] == 'verde').sum()}")
    viv_fuera = fuera["TVIVPAR"].sum()
    if pd.notna(viv_fuera) and viv_fuera > 0:
        print(f"  fuera del agregado: {int(viv_fuera):,} viviendas en AGEB con dato reservado")

print("\n" + "=" * 72)
print("TOP 10 AGEB, PLAYA DEL CARMEN")
print("=" * 72)
t10 = pdc.head(10)[["cvegeo", "TVIVPAR", "VIVPAR_HAB", "VIVPAR_UT", "vivpar_ut_pct", "semaforo_ut"]]
print(t10.to_string(index=False))

print("\n=== FRANJA DE APROXIMACION, 6 a 8% (la lista que importa) ===")
fr = pdc[pdc["semaforo_ut"] == "ambar"][["cvegeo", "TVIVPAR", "VIVPAR_UT", "vivpar_ut_pct"]]
print(fr.to_string(index=False) if len(fr) else "  ninguna")

# --- mapa ---
gj = json.loads(df[cols + ["geometry"]].to_json())
html = """<!doctype html><meta charset="utf-8">
<title>Uso temporal de vivienda por AGEB, Solidaridad</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
 body{margin:0;font:14px/1.5 system-ui,sans-serif}
 #map{height:100vh}
 .box{position:absolute;top:12px;right:12px;z-index:1000;background:#fff;padding:14px 16px;
      max-width:330px;box-shadow:0 2px 12px rgba(0,0,0,.2);border-radius:6px}
 h1{font-size:15px;margin:0 0 6px}
 p{margin:6px 0;font-size:12px;color:#333}
 .k{display:flex;align-items:center;gap:7px;margin:3px 0;font-size:12px}
 .sw{width:15px;height:15px;border:1px solid #999}
 .warn{background:#fff6e5;border-left:3px solid #e8a33d;padding:7px 9px;font-size:11px;margin-top:9px}
</style>
<div id="map"></div>
<div class="box">
  <h1>Vivienda de uso temporal por AGEB</h1>
  <p>Solidaridad, Quintana Roo. Censo 2020 (INEGI), VIVPAR_UT / TVIVPAR.</p>
  <div class="k"><span class="sw" style="background:#c0392b"></span> Sobre 8% (umbral de referencia de Málaga)</div>
  <div class="k"><span class="sw" style="background:#e8a33d"></span> Franja de aproximación, 6 a 8%</div>
  <div class="k"><span class="sw" style="background:#3d8b5f"></span> Bajo 6%</div>
  <div class="k"><span class="sw" style="background:#cccccc"></span> Sin dato censal (reservado)</div>
  <div class="warn">
    Esto <b>no es</b> el índice de penetración de renta vacacional. Es el control censal
    de uso temporal. El índice requiere listings georreferenciados, que esta corrida no levantó.
    Denominador censal 2020: el parque creció desde entonces.
    El 8% es umbral de referencia de Málaga, <b>no norma local</b>. En Quintana Roo no existe norma local.
  </div>
</div>
<script>
const data = __GEOJSON__;
const map = L.map('map').setView([20.66, -87.08], 12);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  {attribution:'&copy; OpenStreetMap, &copy; CARTO', maxZoom:19}).addTo(map);
const color = s => s==='rojo'?'#c0392b':s==='ambar'?'#e8a33d':s==='verde'?'#3d8b5f':'#cccccc';
const layer = L.geoJSON(data, {
  style: f => ({fillColor: color(f.properties.semaforo_ut), fillOpacity:.65,
                color:'#fff', weight:1}),
  onEachFeature: (f,l) => {
    const p = f.properties;
    const pct = p.vivpar_ut_pct==null ? 'sin dato' : p.vivpar_ut_pct.toFixed(2)+'%';
    l.bindPopup(`<b>AGEB ${p.cvegeo}</b><br>${p.localidad||''}<br><br>
      Viviendas particulares: <b>${p.TVIVPAR??'sin dato'}</b><br>
      De uso temporal: <b>${p.VIVPAR_UT??'sin dato'}</b><br>
      Uso temporal: <b>${pct}</b><br>
      <span style="color:#888;font-size:11px">Censo 2020. No es el índice de renta vacacional.</span>`);
  }
}).addTo(map);
map.fitBounds(layer.getBounds());
</script>"""
(OUT / "mapa.html").write_text(html.replace("__GEOJSON__", json.dumps(gj)), encoding="utf-8")
print(f"\nmapa.html y ageb_solidaridad.geojson escritos en {OUT}")
