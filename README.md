# Editor de Plantillas QGIS

Este repositorio contiene una aplicación PyQt5 diseñada para modificar dinámicamente plantillas QGIS (.qpt) basadas en la entrada del usuario y realizar operaciones geoespaciales utilizando QGIS.

## Características

- Interfaz gráfica para la entrada de datos relacionados con expedientes catastrales.
- Descarga y procesamiento de archivos KML desde un servidor remoto.
- Modificación de plantillas QGIS (.qpt) para actualizar campos como títulos, referencias y fuentes.
- Cálculos geoespaciales para ajustar componentes en la plantilla basándose en el centroide de las capas procesadas.
- Guarda los resultados en formatos SHP y KML y los carga en un proyecto QGIS.

## Requisitos

Para ejecutar esta aplicación, necesitas tener instalado:

- Python 3.x
- PyQt5
- QGIS con el módulo `processing` habilitado

Puedes instalar PyQt5 usando pip:

```bash
pip install PyQt5
