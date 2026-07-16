"""
Genera una imagen con Google Imagen (Vertex AI) a partir de un prompt de texto,
y la sube a un bucket público de Google Cloud Storage para obtener una URL
pública (requerida por Instagram y TikTok).

Requiere:
  pip install google-cloud-aiplatform google-cloud-storage
  Variable de entorno GOOGLE_APPLICATION_CREDENTIALS apuntando al JSON de la
  cuenta de servicio (ver README).
"""

import uuid
import datetime

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.cloud import storage

import config


def generate_image(prompt: str) -> bytes:
    vertexai.init(project=config.GCP_PROJECT_ID, location=config.GCP_LOCATION)
    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

    result = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_some",
        person_generation="allow_adult",
    )
    image = result.images[0]
    return image._image_bytes


def upload_to_public_bucket(image_bytes: bytes) -> str:
    """Sube la imagen a GCS y devuelve una URL pública."""
    client = storage.Client(project=config.GCP_PROJECT_ID)
    bucket = client.bucket(config.GCS_BUCKET_NAME)

    today = datetime.date.today().isoformat()
    filename = f"posts/{today}-{uuid.uuid4().hex[:8]}.png"
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")
    blob.make_public()

    return blob.public_url


def generate_and_host_image(prompt: str) -> str:
    """Genera la imagen y devuelve su URL pública lista para usar en las APIs."""
    image_bytes = generate_image(prompt)
    return upload_to_public_bucket(image_bytes)
