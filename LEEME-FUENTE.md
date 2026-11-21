# Geneticapedia: código fuente

Rama `fuente`: generador y contenidos. La rama `main` contiene solo el sitio generado (dist/).

- Contenido: src/{es,en}/<sección>/NN-slug.md. Blog: src/{es,en}/blog/AAAA-MM-DD-slug.md (clave `en:` en el post ES con el slug EN; `tipo: breve` para noticias breves).
- Créditos de imágenes: src/imagenes.json.
- Generar: `python3 build.py` (escribe dist/).
- Publicar: copiar dist/. a un clon de `main`, commit y push; después, despliegue git de Hostinger (dominio geneticapedia.com, rama main, directorio vacío).
