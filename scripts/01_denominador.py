"""Denominador censal por AGEB urbana, Solidaridad (MUN 008).

Fuente: INEGI, Censo 2020, Principales resultados por AGEB y manzana urbana (SCITEL),
archivo RESAGEBURB_23CSV20.csv, entidad 23 Quintana Roo.

Salida: output/denominador_solidaridad.csv
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "censo_23" / "RESAGEBURB_23CSV20.csv"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

CAMPOS = ["TVIVPAR", "VIVPAR_HAB", "VIVPAR_DES", "VIVPAR_UT"]

df = pd.read_csv(SRC, dtype=str, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

# Fila de AGEB agregada, no manzanas. El descriptor la marca con NOM_LOC = "Total AGEB urbana".
sol = df[(df["MUN"] == "008") & (df["NOM_LOC"] == "Total AGEB urbana")].copy()
print(f"AGEB urbanas en Solidaridad: {len(sol)}")

# Confidencialidad: INEGI reserva celdas con '*' y marca no aplica con 'N/D'.
# Se cuentan las perdidas por AGEB antes de convertir a numero.
reservados = {}
for c in CAMPOS:
    marca = sol[c].isin(["*", "N/D"]) | sol[c].isna()
    reservados[c] = int(marca.sum())
    sol[c] = pd.to_numeric(sol[c].where(~marca), errors="coerce")

sol["celdas_reservadas"] = sol[CAMPOS].isna().sum(axis=1)

# Una AGEB solo es rankeable si tiene AMBOS terminos del cociente. Si el Censo reservo
# VIVPAR_UT, el porcentaje no existe, aunque TVIVPAR si este. No se imputa.
sol["sin_dato_censal"] = (
    sol["TVIVPAR"].isna() | (sol["TVIVPAR"] == 0) | sol["VIVPAR_UT"].isna()
)

# Clave AGEB completa de 13 digitos: ENT(2) MUN(3) LOC(4) AGEB(4)
sol["cvegeo"] = sol["ENTIDAD"].str.zfill(2) + sol["MUN"].str.zfill(3) + sol["LOC"].str.zfill(4) + sol["AGEB"].astype(str)

sol["vivpar_ut_pct"] = (sol["VIVPAR_UT"] / sol["TVIVPAR"] * 100).round(2)

cols = ["cvegeo", "ENTIDAD", "MUN", "LOC", "AGEB", "POBTOT",
        "TVIVPAR", "VIVPAR_HAB", "VIVPAR_DES", "VIVPAR_UT",
        "vivpar_ut_pct", "celdas_reservadas", "sin_dato_censal"]
sol = sol[cols].sort_values("cvegeo")
sol.to_csv(OUT / "denominador_solidaridad.csv", index=False)

print("\n=== Confidencialidad: celdas reservadas por campo ===")
for c, n in reservados.items():
    print(f"  {c}: {n} de {len(sol)} AGEB")

solo_tv = int((sol["TVIVPAR"].notna() & (sol["TVIVPAR"] > 0) & sol["VIVPAR_UT"].isna()).sum())
sin_tv = int((sol["TVIVPAR"].isna() | (sol["TVIVPAR"] == 0)).sum())
print(f"\nAGEB sin TVIVPAR (denominador reservado): {sin_tv}")
print(f"AGEB con TVIVPAR pero VIVPAR_UT reservado: {solo_tv}")
print(f"AGEB no rankeables en total: {int(sol['sin_dato_censal'].sum())}")

rank = sol[~sol["sin_dato_censal"]]
print(f"AGEB rankeables (ambos terminos presentes): {len(rank)}")
# El agregado se calcula SOLO sobre AGEB con ambos terminos. Meter el TVIVPAR de una AGEB
# cuyo VIVPAR_UT esta reservado subestimaria el cociente.
print(f"\nSobre las AGEB rankeables:")
print(f"  TVIVPAR: {int(rank['TVIVPAR'].sum()):,}")
print(f"  VIVPAR_UT: {int(rank['VIVPAR_UT'].sum()):,}")
print(f"  Uso temporal como % del parque: {rank['VIVPAR_UT'].sum() / rank['TVIVPAR'].sum() * 100:.2f}%")
excl = sol[sol["sin_dato_censal"]]["TVIVPAR"].sum()
print(f"  (quedan fuera del agregado {int(excl):,} viviendas en AGEB no rankeables)")

print("\n=== Top 10 AGEB por VIVPAR_UT / TVIVPAR (control censal, NO es el indice) ===")
top = rank.nlargest(10, "vivpar_ut_pct")[["cvegeo", "TVIVPAR", "VIVPAR_UT", "vivpar_ut_pct"]]
print(top.to_string(index=False))

# Localidades: la pregunta abierta 3 del brief.
print("\n=== Localidades dentro de Solidaridad (mancha urbana vs no conurbadas) ===")
locs = df[(df["MUN"] == "008") & (df["NOM_LOC"] == "Total AGEB urbana")].groupby("LOC").size()
nombres = (df[(df["MUN"] == "008") & (df["MZA"] == "000") & (df["AGEB"] == "0000")]
           .set_index("LOC")["NOM_LOC"].to_dict())
for loc, n in locs.items():
    print(f"  LOC {loc}: {n} AGEB  ({nombres.get(loc, 'nombre no resuelto')})")
