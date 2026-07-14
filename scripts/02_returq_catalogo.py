"""Catalogo Oficial de Prestadores de Servicios (RETUR-Q / SITUR-Q).

Fuente: https://siturq.gob.mx/catalogo-oficial (HTML renderizado en servidor).
Captura: 12 de julio de 2026.

Las fichas traen data-id, data-name, data-municipality y data-category.
NO traen domicilio ni coordenadas, asi que NO sirven como numerador georreferenciado.
Se levanta igual porque el conteo de hospedaje registrado contra el inventario
de mercado es, por si solo, la medida de la brecha de cumplimiento.

Salida: output/returq_catalogo.csv
"""
import re
import csv
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
URL = "https://siturq.gob.mx/catalogo-oficial"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (research; INEGI AGEB study)"})
html_text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

# Catalogo de categorias, del <select> de filtros
cats = dict(re.findall(r'<option value="([0-9a-f-]{36})">([^<]+)</option>', html_text))

card_re = re.compile(
    r'<div class="card"\s+data-id="(?P<id>[^"]*)"\s+data-name="(?P<name>[^"]*)"\s+'
    r'data-municipality="(?P<mun>[^"]*)"\s+data-destination="(?P<dest>[^"]*)"\s+'
    r'data-category="(?P<cat>[^"]*)"',
    re.S,
)
rows = []
for m in card_re.finditer(html_text):
    d = m.groupdict()
    rows.append({
        "id": d["id"],
        "nombre": d["name"].strip(),
        "municipio": d["mun"].strip(),
        "categoria": cats.get(d["cat"], d["cat"]),
    })

with open(OUT / "returq_catalogo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "nombre", "municipio", "categoria"])
    w.writeheader()
    w.writerows(rows)

print(f"Prestadores en el catalogo publico: {len(rows)}")

from collections import Counter
print("\n=== Hospedaje por municipio ===")
hosp = [r for r in rows if r["categoria"] == "Hospedaje"]
for mun, n in Counter(r["municipio"] for r in hosp).most_common():
    print(f"  {mun:28s} {n:>5}")
print(f"\nTotal hospedaje registrado en el estado: {len(hosp)}")

pdc = [r for r in hosp if r["municipio"] == "Playa del Carmen"]
print(f"Hospedaje registrado en Playa del Carmen: {len(pdc)}")

print("\n=== Todas las categorias ===")
for c, n in Counter(r["categoria"] for r in rows).most_common(8):
    print(f"  {c:38s} {n:>5}")
