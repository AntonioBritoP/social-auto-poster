"""
Orquesta el flujo completo de una publicación automática.

Cada corrida elige, según config.INVENTORY_POST_PROBABILITY, entre:

  A) Publicación de INVENTARIO: usa foto(s) REAL(es) de un auto (de
     inventory.json + tu bucket de GCS) y un caption con datos reales.
       - Instagram/Facebook: se publica la primera foto del auto.
       - TikTok: se arma un VIDEO automático con TODAS las fotos del auto
         (efecto Ken Burns + texto overlay con los datos reales).

  B) Publicación GENÉRICA: usa una imagen generada por IA (Google Imagen)
     para contenido educativo/institucional, sin mostrar ningún auto
     específico como si estuviera en venta. En este modo TikTok recibe esa
     misma imagen como una foto fija (no arma video).
"""

import os
import random
import shutil
import sys
import tempfile
import traceback

import build_video
import config
import generate_caption
import generate_image
import inventory
import post_meta
import post_tiktok


def run():
    print("=== Iniciando publicación automática ===")

    use_inventory = random.random() < config.INVENTORY_POST_PROBABILITY
    results = {}
    work_dir = tempfile.mkdtemp(prefix="social_post_")

    try:
        if use_inventory:
            print("Modo: publicación de INVENTARIO (fotos reales)")
            car = inventory.pick_car()
            print(f"Auto elegido: {car['marca']} {car['modelo']} {car['anio']}")

            caption = generate_caption.generate_inventory_caption(car)
            print(f"Caption:\n{caption}\n")

            image_url = inventory.photo_public_url(car)  # primera foto, para IG/FB

            # --- Instagram ---
            try:
                results["instagram"] = post_meta.post_to_instagram(image_url, caption)
                print(f"✅ Instagram OK: {results['instagram']}")
            except Exception as e:
                print(f"❌ Error publicando en Instagram: {e}")
                traceback.print_exc()

            # --- Facebook ---
            try:
                results["facebook"] = post_meta.post_to_facebook(image_url, caption)
                print(f"✅ Facebook OK: {results['facebook']}")
            except Exception as e:
                print(f"❌ Error publicando en Facebook: {e}")
                traceback.print_exc()

            # --- TikTok: arma video real con todas las fotos del auto ---
            try:
                print("Descargando fotos del auto para armar el video...")
                photo_paths = inventory.download_photos_locally(car, work_dir)
                print(f"Armando video con {len(photo_paths)} foto(s)...")
                video_path = build_video.build_video_for_car(car, photo_paths)
                results["tiktok"] = post_tiktok.post_video(video_path, caption)
                print(f"✅ TikTok OK: {results['tiktok']}")
            except Exception as e:
                print(f"❌ Error publicando en TikTok: {e}")
                traceback.print_exc()

        else:
            print("Modo: publicación GENÉRICA (imagen de IA)")
            theme = generate_caption.pick_theme()
            print(f"Tema elegido: {theme}")
            content = generate_caption.generate_caption(theme)
            caption = content["caption"]
            print(f"Caption:\n{caption}\n")
            image_url = generate_image.generate_and_host_image(content["image_prompt"])
            print(f"Imagen generada: {image_url}")

            try:
                results["instagram"] = post_meta.post_to_instagram(image_url, caption)
                print(f"✅ Instagram OK: {results['instagram']}")
            except Exception as e:
                print(f"❌ Error publicando en Instagram: {e}")
                traceback.print_exc()

            try:
                results["facebook"] = post_meta.post_to_facebook(image_url, caption)
                print(f"✅ Facebook OK: {results['facebook']}")
            except Exception as e:
                print(f"❌ Error publicando en Facebook: {e}")
                traceback.print_exc()

            # Contenido genérico: no hay fotos reales de un auto que animar
            # en video, así que este modo solo publica en Instagram/Facebook.
            print(
                "ℹ️  TikTok: el contenido genérico no genera video (solo aplica "
                "al modo inventario). Esta publicación no se manda a TikTok."
            )

        print("=== Resumen ===")
        print(results)

        if not results:
            sys.exit(1)  # nada se publicó -> marca el run como fallido

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    run()
