"""
Publica un video en TikTok usando el Content Posting API, subiendo el archivo
directamente (FILE_UPLOAD) en vez de desde una URL pública.

IMPORTANTE: la publicación directa (post_mode="DIRECT_POST") requiere que tu
app haya pasado la revisión de "Direct Post" de TikTok. Mientras esa revisión
no esté aprobada, TikTok solo permite post_mode="MEDIA_UPLOAD", que manda el
video a favoritos/borradores de la cuenta para que TÚ lo publiques manualmente
desde la app de TikTok. Este script usa MEDIA_UPLOAD por default para que
funcione desde ya; cuando tengas la aprobación de Direct Post, cambia
POST_MODE abajo a "DIRECT_POST" para que se publique 100% solo.

Documentación oficial (revisar antes de usar en producción, cambia con el
tiempo): https://developers.tiktok.com/doc/content-posting-api-get-started
"""

import os
import requests

import config

BASE_URL = "https://open.tiktokapis.com/v2"

# Cambia a "DIRECT_POST" una vez que tu app tenga aprobado el acceso de
# publicación directa. Mientras tanto, "MEDIA_UPLOAD" manda el video a la
# bandeja de tu cuenta de TikTok para que lo publiques tú con un toque.
POST_MODE = "MEDIA_UPLOAD"


def post_video(video_path: str, caption: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    file_size = os.path.getsize(video_path)

    body = {
        "post_info": {
            "title": caption,
            "privacy_level": "PUBLIC_TO_EVERYONE" if POST_MODE == "DIRECT_POST" else "SELF_ONLY",
            "disable_comment": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1,
        },
        "post_mode": POST_MODE,
        "media_type": "VIDEO",
    }

    endpoint = "video" if POST_MODE == "DIRECT_POST" else "inbox/video"
    init_resp = requests.post(
        f"{BASE_URL}/post/publish/{endpoint}/init/",
        headers=headers,
        json=body,
    )
    init_resp.raise_for_status()
    init_data = init_resp.json()

    if init_data.get("error", {}).get("code") not in (None, "ok"):
        raise RuntimeError(f"Error iniciando publicación en TikTok: {init_data['error']}")

    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
        "Content-Type": "video/mp4",
    }
    upload_resp = requests.put(upload_url, headers=upload_headers, data=video_bytes)
    upload_resp.raise_for_status()

    return publish_id
