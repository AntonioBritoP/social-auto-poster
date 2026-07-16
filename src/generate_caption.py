"""
Genera el texto (caption) de la publicación usando la API de Anthropic (Claude).
"""

import json
import random
import urllib.request

import config


def generate_caption(theme: str) -> dict:
    """
    Devuelve un dict con:
      - caption: texto listo para publicar (incluye hashtags)
      - image_prompt: descripción en inglés para pedirle la imagen a Imagen
    """
    system_prompt = (
        f"Eres el community manager de la marca '{config.BRAND_NAME}'. "
        f"Contexto de la marca: {config.BRAND_DESCRIPTION}\n\n"
        "Tu tarea: generar UNA publicación para redes sociales sobre el tema "
        f"indicado. Responde ÚNICAMENTE con un JSON válido (sin texto extra, "
        "sin markdown) con esta forma exacta:\n"
        '{"caption": "texto del post en español con 3-5 hashtags relevantes al final", '
        '"image_prompt": "descripción en inglés, detallada, de una imagen fotográfica '
        'o ilustración que acompañe el post (sin texto/letras dentro de la imagen)"}'
    )

    user_prompt = f"Tema de hoy: {theme}"

    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 600,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    text = "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    )
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def generate_inventory_caption(car: dict) -> str:
    """
    Genera el caption para una publicación de un auto REAL del inventario.
    Usa solo los datos provistos en `car` — nunca inventa specs.
    """
    system_prompt = (
        f"Eres el community manager de la marca '{config.BRAND_NAME}'. "
        f"Contexto de la marca: {config.BRAND_DESCRIPTION}\n\n"
        "Tu tarea: escribir el caption para publicar la foto de un auto real "
        "disponible en venta, usando ÚNICAMENTE los datos exactos que te doy "
        "(no inventes ni agregues características que no se mencionan). "
        "Tono profesional y serio. Incluye un llamado a la acción para "
        "contactar/cotizar, y 3-5 hashtags relevantes al final. "
        "Responde ÚNICAMENTE con el texto del caption, sin comillas ni "
        "explicaciones adicionales."
    )

    user_prompt = (
        f"Marca: {car['marca']}\n"
        f"Modelo: {car['modelo']}\n"
        f"Año: {car['anio']}\n"
        f"Kilometraje: {car['kilometraje_km']} km\n"
        f"Precio: ${car['precio_mxn']:,} MXN\n"
        f"Estado/notas: {car['estado']}"
    )

    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 400,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    return "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    ).strip()


def pick_theme() -> str:
    return random.choice(config.GENERIC_THEMES)
