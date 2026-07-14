# Uso temporal de vivienda por AGEB - Solidaridad, Quintana Roo

Pipeline abierto y reproducible que mide el peso de la **vivienda particular de uso
temporal** sobre el parque residencial total, AGEB por AGEB, en el municipio de
Solidaridad (Playa del Carmen y Puerto Aventuras), con datos del Censo de Población
y Vivienda 2020 del INEGI.

Es la metodología completa detrás del artículo *"Medir a tiempo: Playa del Carmen
estrena su primer índice de vivienda de uso temporal por zona"*, publicado en
Riviera Maya Economic Pulse. Cualquier persona puede correr estos scripts sobre las
fuentes públicas citadas y llegar exactamente al mismo número.

## Qué mide, y qué no

**Mide:** la proporción `VIVPAR_UT / TVIVPAR` por AGEB urbana, es decir, qué fracción
de las viviendas particulares de cada polígono censal quedó registrada como de uso
temporal en el Censo 2020.

**No mide:** renta vacacional activa. El uso temporal censal es el proxy oficial más
cercano y con cobertura completa que existe, pero incluye también segundas residencias
no rentadas. No es un conteo de listings de Airbnb ni un padrón de anfitriones. La
columna `penetracion_pct` existe en las salidas y está deliberadamente vacía: ese
índice requiere listings georreferenciados, que este pipeline no levanta.

## Resultados centrales (verificables sobre los datos de este repo)

| Indicador | Valor |
|---|---|
| Uso temporal agregado, Playa del Carmen | **10.82%** |
| AGEB de Playa del Carmen sobre el umbral de 8% | **59 de 147** con dato censal |
| Uso temporal agregado, Puerto Aventuras | **13.07%** |
| AGEB urbanas totales en Solidaridad | 175 (156 rankeables, 19 reservadas) |

El **8%** es el umbral de referencia que el Ayuntamiento de Málaga (2024-2025) usó
para cerrar barrios a nueva vivienda turística. Se cita como contexto internacional,
**no como norma local**: en Quintana Roo no existe hoy una norma equivalente.

## Cifras censales usadas en la proyección 2010→2026

Las proyecciones a 2026 del artículo se calculan con las tasas de crecimiento anual
compuesto (CAGR) de las series municipales del ITER entre los Censos 2010 y 2020,
entidad 23 (Quintana Roo), municipio 008 (Solidaridad):

| Serie | 2010 | 2020 | CAGR anual |
|---|---|---|---|
| Viviendas particulares totales | **68,471** | **124,631** | 6.17% |
| Viviendas particulares de uso temporal | **6,170** | **13,385** | 8.05% |

- **Escenario conservador** (numerador constante sobre denominador proyectado): ≈7.5%,
  presentado como cota inferior.
- **Escenario tendencial** (cada serie a su propia tasa): ≈11.9%.
- **Dato duro** (Censo 2020): 10.82%.

Las proyecciones son cotas de lectura, no estimaciones puntuales, y se declaran
siempre como cálculo propio, no como dato oficial.

## Confidencialidad censal

El INEGI reserva celdas por confidencialidad estadística. Una AGEB solo es rankeable
si tiene **ambos** términos del cociente: si el Censo reservó `VIVPAR_UT`, el
porcentaje no existe y **no se imputa**. De las 175 AGEB urbanas, 19 quedan fuera del
ranking (marcadas con `sin_dato_censal = True` y en gris en el mapa). El agregado se
calcula solo sobre las AGEB rankeables, para no meter viviendas en el denominador sin
su contraparte en el numerador.

## El pipeline

Cuatro scripts de Python sobre fuentes públicas y gratuitas, sin credenciales:

| Script | Qué hace | Salida |
|---|---|---|
| `scripts/01_denominador.py` | Denominador censal por AGEB, filtro de municipio y manejo de confidencialidad | `output/denominador_solidaridad.csv` |
| `scripts/02_returq_catalogo.py` | Levanta el conteo del Catálogo Oficial público de prestadores (SITUR-Q) | conteo agregado (ver nota) |
| `scripts/03_tabla_y_mapa.py` | Une con los polígonos del Marco Geoestadístico, calcula el semáforo, genera tabla, GeoJSON y mapa interactivo | `output/ageb_solidaridad.csv`, `.geojson`, `mapa.html` |
| `scripts/04_colonias.py` | Colonia aproximada por geocodificación inversa del centroide (Nominatim) | `output/top_ageb_con_colonia.csv` |

> Nota sobre `02`: el Catálogo Oficial público es, por mandato del artículo 52 Nonies
> de la Ley de Turismo de Quintana Roo, únicamente el subconjunto de prestadores que
> autorizaron expresamente su difusión. El conteo que arroja es un **piso, no el
> padrón completo**, y por eso no se deriva de él ninguna tasa de cumplimiento. Este
> repo no redistribuye el catálogo (contiene nombres de personas físicas); el script
> documenta cómo regenerarlo desde la fuente pública.

### Cómo correrlo

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install pandas geopandas matplotlib tabulate
# Descarga las fuentes INEGI en data/ (ver data/README.md), luego:
python3 scripts/01_denominador.py
python3 scripts/03_tabla_y_mapa.py
python3 scripts/04_colonias.py   # requiere conexión (Nominatim)
```

## Salidas incluidas

En `output/` se incluyen las salidas agregadas por AGEB (datos censales derivados,
sin información personal):

- `denominador_solidaridad.csv` - denominador censal por AGEB con marcas de confidencialidad
- `ageb_solidaridad.csv` - tabla final por AGEB con porcentaje y semáforo
- `ageb_solidaridad.geojson` - lo mismo, con los polígonos, para reproducir el mapa
- `top_ageb_con_colonia.csv` - top 10 y franja 6-8% con colonia aproximada

## Fuentes

- **Censo de Población y Vivienda 2020**, INEGI - Principales resultados por AGEB y
  manzana urbana (SCITEL), archivo `RESAGEBURB_23CSV20.csv`, entidad 23.
- **Marco Geoestadístico**, INEGI, diciembre 2020 - polígonos de AGEB urbana, capa `23a`.
- **ITER 2010**, INEGI - series municipales para las tasas de crecimiento.
- **Catálogo Oficial de Prestadores de Servicios**, SITUR-Q (`siturq.gob.mx`).
- **Umbral del 8%** - Ayuntamiento de Málaga, referencia externa.

Corte del análisis: julio de 2026.

## Licencia

- **Código** (`scripts/`): MIT. Ver [LICENSE](LICENSE).
- **Datos derivados** (`output/`): CC BY 4.0. Al reutilizarlos, cita la fuente
  primaria (INEGI, Censo 2020) y este repositorio.

Los datos originales del INEGI son de uso libre en los términos de su propia licencia.

---

Riviera Maya Economic Pulse
