"""
Publica una imagen + caption en Instagram y Facebook usando la Graph API de Meta.

Requisitos previos (se hacen UNA SOLA VEZ, fuera de este script):
  1. Cuenta de Instagram tipo Business/Creator, vinculada a una Página de Facebook.
  2. App creada en developers.facebook.com con permisos:
     instagram_content_publish, pages_manage_posts, pages_read_engagement
  3. Token de acceso de Página (de larga duración, ~60 días, renovable).

Documentación oficial (revisar siempre la versión vigente antes de usar en
producción, la API cambia con el tiempo):
  https://developers.facebook.com/docs/instagram-api/guides/content-publishing
  https://developers.facebook.com/docs/pages-api/posts
"""

import time
import requests

import config

GRAPH_URL = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}"


def post_to_instagram(image_url: str, caption: str) -> str:
    # 1. Crear el "media container"
    container_resp = requests.post(
        f"{GRAPH_URL}/{config.META_IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": config.META_PAGE_ACCESS_TOKEN,
        },
    )
    container_resp.raise_for_status()
    creation_id = container_resp.json()["id"]

    # Pequeña espera para que Meta termine de procesar la imagen
    time.sleep(5)

    # 2. Publicar el container
    publish_resp = requests.post(
        f"{GRAPH_URL}/{config.META_IG_USER_ID}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": config.META_PAGE_ACCESS_TOKEN,
        },
    )
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]


def post_to_facebook(image_url: str, caption: str) -> str:
    resp = requests.post(
        f"{GRAPH_URL}/{config.META_PAGE_ID}/photos",
        data={
            "url": image_url,
            "caption": caption,
            "access_token": config.META_PAGE_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]
