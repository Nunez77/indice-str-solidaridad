# Datos de origen (no incluidos en el repo)

Los scripts esperan aquí las fuentes públicas del INEGI. No se redistribuyen en este
repositorio por tamaño; se descargan gratis del INEGI y se colocan en las rutas que
cada script espera.

## 1. Censo 2020 - Principales resultados por AGEB y manzana urbana (Quintana Roo)

- Producto: INEGI, Censo de Población y Vivienda 2020, "Principales resultados por AGEB
  y manzana urbana" (SCITEL), entidad 23 Quintana Roo.
- Archivo esperado: `data/censo_23/RESAGEBURB_23CSV20.csv`
- Lo usa: `01_denominador.py`

## 2. Marco Geoestadístico 2020 - Quintana Roo

- Producto: INEGI, Marco Geoestadístico, diciembre 2020, entidad 23.
- Shapefile de AGEB urbana esperado en: `data/mg23/conjunto_de_datos/23a.shp`
  (con sus `.dbf`, `.shx`, `.prj`, `.cpg`).
- Lo usa: `03_tabla_y_mapa.py`

## 3. ITER 2010 - Quintana Roo (o nacional)

- Producto: INEGI, Censo 2010, Iteradores (ITER).
- Usado para las series municipales 2010 (68,471 viviendas particulares totales;
  6,170 de uso temporal) que alimentan las tasas de crecimiento del artículo.

## Verificación sin correr los scripts

Si solo quieres verificar los números publicados sin descargar las fuentes crudas,
las salidas agregadas ya están en `output/`. Puedes cotejar el agregado de Playa del
Carmen (10.82%), el conteo de AGEB sobre 8% (59) y el de Puerto Aventuras (13.07%)
directamente sobre `output/ageb_solidaridad.csv`.
