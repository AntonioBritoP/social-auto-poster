"""
Configuración central del bot de publicación automática.

Todos los valores sensibles (tokens, keys) se leen de variables de entorno
(GitHub Secrets cuando corre en GitHub Actions). NUNCA pongas tokens directamente
en este archivo.
"""

import os

# ---------------------------------------------------------------------------
# IDENTIDAD DE TU MARCA / NEGOCIO
# Ajusta esto a tu negocio. Es lo que usa la IA para generar imágenes y textos
# coherentes con tu marca en cada publicación.
# ---------------------------------------------------------------------------
BRAND_NAME = "Tu Agencia de Autos"  # <-- cambia esto por el nombre real de tu negocio
BRAND_DESCRIPTION = (
    "Venta de autos usados y americanos legalizados (importados de EE.UU. y "
    "legalizados en México, listos para circular). Tono de voz profesional y "
    "serio, que transmita confianza y seguridad en la compra. Público "
    "objetivo: personas buscando un auto usado en buen estado, con la "
    "tranquilidad de que está correctamente legalizado y documentado."
)

# ---------------------------------------------------------------------------
# DOS TIPOS DE PUBLICACIÓN:
#
# 1. GENERIC_THEMES -> usan imagen generada por IA (Google Imagen).
#    Solo para contenido educativo/institucional donde NO se muestra un auto
#    específico de venta (para no mostrar un auto "falso" como si fuera real).
#
# 2. INVENTORY_THEMES -> usan una FOTO REAL de un auto, tomada de tu archivo
#    inventory.json (ver inventory.json en la raíz del proyecto). El caption
#    se genera con los datos reales de ese auto, nunca inventados.
# ---------------------------------------------------------------------------

GENERIC_THEMES = [
    "ventajas de comprar un auto americano legalizado vs uno sin legalizar",
    "el proceso de legalización explicado de forma simple y confiable",
    "tips para elegir un buen auto usado (qué revisar antes de comprar)",
    "garantías, documentación y respaldo que ofrece la agencia",
    "financiamiento o facilidades de pago disponibles",
]

INVENTORY_THEMES = [
    "presentar un auto disponible del inventario actual",
]

# Probabilidad de que una publicación sea de inventario (foto real) vs
# genérica (imagen de IA). 0.7 = 70% de las publicaciones muestran un auto
# real en venta, 30% es contenido educativo genérico.
INVENTORY_POST_PROBABILITY = 0.7

# Ruta al archivo con tu inventario actual (ver inventory.json de ejemplo).
INVENTORY_FILE = "inventory.json"

# Prefijo dentro de tu bucket de GCS donde subes las fotos reales de los autos.
# Ejemplo: si subes una foto a gs://tu-bucket/inventario/auto1.jpg, el
# "photo_filename" en inventory.json debe ser "auto1.jpg".
GCS_INVENTORY_PREFIX = "inventario"

# ---------------------------------------------------------------------------
# GOOGLE IMAGEN (Vertex AI) - generación de imágenes
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
# La autenticación se hace vía GOOGLE_APPLICATION_CREDENTIALS (archivo JSON
# de cuenta de servicio) - ver README para cómo configurarlo como secret.

# ---------------------------------------------------------------------------
# ANTHROPIC (Claude) - generación de captions/texto
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ---------------------------------------------------------------------------
# META (Instagram + Facebook) - Graph API
# ---------------------------------------------------------------------------
META_PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN")
META_PAGE_ID = os.environ.get("META_PAGE_ID")
META_IG_USER_ID = os.environ.get("META_IG_USER_ID")
GRAPH_API_VERSION = "v19.0"

# ---------------------------------------------------------------------------
# TIKTOK - Content Posting API
# TikTok publica un VIDEO armado automáticamente a partir de las fotos reales
# del auto (efecto Ken Burns + texto con los datos reales), no una imagen fija.
# Ver src/build_video.py y src/post_tiktok.py.
# ---------------------------------------------------------------------------
TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN")

# ---------------------------------------------------------------------------
# ALMACENAMIENTO PÚBLICO DE IMÁGENES
# Instagram y TikTok requieren que la imagen esté en una URL pública antes
# de publicarla. Usamos un bucket de Google Cloud Storage para esto.
# ---------------------------------------------------------------------------
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
