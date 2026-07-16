"""
Arma un video vertical (formato TikTok, 1080x1920) a partir de fotos REALES
de un auto del inventario, con efecto Ken Burns (zoom/paneo suave) en cada
foto y un texto overlay con los datos reales del auto.

Requiere ffmpeg instalado en el sistema (ya viene preinstalado en la imagen
de GitHub Actions ubuntu-latest, no necesitas instalar nada aparte).
"""

import os
import subprocess
import tempfile

SECONDS_PER_PHOTO = 3
FPS = 30
WIDTH, HEIGHT = 1080, 1920


def _build_kenburns_filter(num_photos: int) -> str:
    """
    Genera el filtro de ffmpeg que aplica zoom/paneo suave a cada foto y las
    concatena. Alterna la dirección del zoom para que no se vea repetitivo.
    """
    frames_per_photo = SECONDS_PER_PHOTO * FPS
    filters = []
    labels = []

    for i in range(num_photos):
        zoom_in = i % 2 == 0
        if zoom_in:
            zoom_expr = f"zoom+0.0015"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        else:
            zoom_expr = f"if(lte(zoom,1.0),1.15,zoom-0.0015)"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        filters.append(
            f"[{i}:v]scale=8000:-1,"
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':"
            f"d={frames_per_photo}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"trim=duration={SECONDS_PER_PHOTO}[v{i}]"
        )
        labels.append(f"[v{i}]")

    concat_filter = f"{''.join(labels)}concat=n={num_photos}:v=1:a=0[outv]"
    filters.append(concat_filter)

    return ";".join(filters)


def build_video(
    photo_paths: list[str],
    overlay_lines: list[str],
    output_path: str,
) -> str:
    """
    photo_paths: rutas locales de las fotos reales, en el orden deseado.
    overlay_lines: líneas de texto con los datos reales del auto (ej.
        ["Ford F-150 2019", "65,000 km", "$385,000 MXN"]) que se muestran
        sobreimpresas en el video.
    output_path: ruta local donde se guardará el .mp4 final.
    """
    if not photo_paths:
        raise ValueError("Se necesita al menos una foto para armar el video")

    filter_complex = _build_kenburns_filter(len(photo_paths))

    # Texto overlay: cada línea centrada, apiladas hacia la parte inferior del
    # video, con fondo semitransparente para que siempre sea legible.
    drawtext_filters = []
    base_y = HEIGHT - 320
    for i, line in enumerate(overlay_lines):
        escaped = line.replace(":", "\\:").replace("'", "\\'")
        fontsize = 64 if i == 0 else 48
        drawtext_filters.append(
            f"drawtext=text='{escaped}':fontcolor=white:fontsize={fontsize}:"
            f"box=1:boxcolor=black@0.55:boxborderw=20:"
            f"x=(w-text_w)/2:y={base_y + i * 80}"
        )

    full_filter = filter_complex + ";[outv]" + ",".join(drawtext_filters) + "[final]"

    cmd = ["ffmpeg", "-y"]
    for path in photo_paths:
        cmd += ["-loop", "1", "-i", path]

    cmd += [
        "-filter_complex", full_filter,
        "-map", "[final]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg falló:\n{result.stderr}")

    return output_path


def build_video_for_car(car: dict, photo_paths: list[str]) -> str:
    """
    Construye las líneas de overlay a partir de los datos reales del auto
    y arma el video. Devuelve la ruta local del .mp4 generado.
    """
    overlay_lines = [
        f"{car['marca']} {car['modelo']} {car['anio']}",
        f"{car['kilometraje_km']:,} km",
        f"${car['precio_mxn']:,} MXN",
    ]

    output_path = os.path.join(tempfile.gettempdir(), f"video_{car['modelo']}.mp4")
    return build_video(photo_paths, overlay_lines, output_path)
