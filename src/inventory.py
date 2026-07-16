"""
Lee el inventario real de autos (inventory.json) y elige uno al azar para
publicar, devolviendo sus datos reales y la URL pública de su foto real
(ya subida por ti a tu bucket de GCS).
"""

import json
import random
import os

import config


def _load_inventory() -> list[dict]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, config.INVENTORY_FILE)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["autos"]


def pick_car() -> dict:
    """Elige un auto al azar del inventario. Lanza error claro si está vacío."""
    autos = _load_inventory()
    if not autos:
        raise ValueError(
            "inventory.json no tiene autos cargados. Agrega al menos uno "
            "antes de correr publicaciones de tipo inventario."
        )
    return random.choice(autos)


def photo_public_url(car: dict, index: int = 0) -> str:
    """
    Construye la URL pública de una foto real del auto en GCS.
    Por default devuelve la primera foto (usada para Instagram/Facebook).
    Requiere que ya hayas subido la foto a:
      gs://{GCS_BUCKET_NAME}/{GCS_INVENTORY_PREFIX}/{filename}
    y que el bucket/objeto sea público.
    """
    filename = car["photo_filenames"][index]
    return (
        f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/"
        f"{config.GCS_INVENTORY_PREFIX}/{filename}"
    )


def all_photo_public_urls(car: dict) -> list[str]:
    """Devuelve las URLs públicas de TODAS las fotos del auto, en orden."""
    return [
        f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/"
        f"{config.GCS_INVENTORY_PREFIX}/{filename}"
        for filename in car["photo_filenames"]
    ]


def download_photos_locally(car: dict, dest_dir: str) -> list[str]:
    """
    Descarga todas las fotos del auto a una carpeta local (necesario para que
    ffmpeg pueda armar el video). Devuelve las rutas locales en orden.
    """
    import os
    import requests

    os.makedirs(dest_dir, exist_ok=True)
    local_paths = []

    for i, url in enumerate(all_photo_public_urls(car)):
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        ext = os.path.splitext(url)[1] or ".jpg"
        local_path = os.path.join(dest_dir, f"photo_{i}{ext}")
        with open(local_path, "wb") as f:
            f.write(resp.content)
        local_paths.append(local_path)

    return local_paths
