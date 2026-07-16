# Bot de publicación automática en redes sociales

Genera imágenes + caption con IA y publica automáticamente en Instagram,
Facebook y TikTok, 3 veces al día, corriendo gratis en GitHub Actions.

## ⚠️ Antes de empezar

- Esto publica **solo en tus propias cuentas**, conectadas con tus propios
  tokens. Es automatización legítima vía las APIs oficiales de cada plataforma,
  no un método para evadir nada — sigue siempre los Términos de Servicio de
  Meta y TikTok (frecuencia razonable, contenido original, sin spam).
- Las APIs de Meta y TikTok cambian con el tiempo. Antes de dejarlo corriendo
  en automático sin supervisión, haz una prueba manual primero (ver paso 6).
- TikTok exige que tu app pase su revisión de "Direct Post" para publicar sin
  intervención manual. **Mientras no esté aprobada** (que es tu caso actual,
  ya que aún no la has solicitado), el bot sube el video a la bandeja de tu
  cuenta de TikTok (`post_mode="MEDIA_UPLOAD"`) y tú lo publicas con un solo
  toque desde la app — no queda público automáticamente. En cuanto TikTok
  apruebe tu Direct Post, cambia `POST_MODE` en `src/post_tiktok.py` de
  `"MEDIA_UPLOAD"` a `"DIRECT_POST"` para que se publique 100% solo.

## Cómo funciona el video de TikTok

Para TikTok, el bot NO usa imágenes generadas por IA — arma un **video real**
a partir de las fotos reales de cada auto (efecto Ken Burns tipo zoom/paneo
suave, con los datos reales del auto sobreimpresos: marca, modelo, año,
kilometraje y precio). Esto evita mostrar contenido falso o engañoso.
Instagram y Facebook siguen publicando la primera foto del auto como imagen
fija.

## Paso 1: Edita tu información de marca y tu inventario real

1. Abre `src/config.py` y cambia `BRAND_NAME` con el nombre real de tu agencia.
2. Abre `inventory.json` y carga tus autos reales disponibles (marca, modelo,
   año, kilometraje, precio, estado, y la lista de fotos en
   `photo_filenames` — agrega varias fotos por auto para que el video de
   TikTok se vea mejor, con distintos ángulos).
3. Sube las **fotos reales** de esos autos a tu bucket de GCS, dentro de la
   carpeta `inventario/` (ej. `gs://tu-bucket/inventario/f150-2019-1.jpg`).
   Cada nombre en `photo_filenames` debe coincidir exactamente con el archivo
   subido.
4. **Cada vez que vendas un auto, bórralo de `inventory.json`** para que el
   bot deje de publicarlo. Cada vez que te llegue inventario nuevo, agrégalo
   con sus fotos.

El bot publica el 70% de las veces un auto real de tu inventario (con su foto
real) y el 30% restante contenido educativo genérico con imagen de IA (tips,
proceso de legalización, financiamiento, etc. — nunca mostrando un auto
"inventado" como si estuviera en venta). Puedes ajustar este porcentaje en
`config.INVENTORY_POST_PROBABILITY`.

## Paso 2: Crea las credenciales de Meta (Instagram + Facebook)

1. Ve a https://developers.facebook.com/apps → "Crear app" → tipo "Business".
2. En "Agregar productos", añade **Instagram Graph API** y **Facebook Login**.
3. En la sección de permisos, solicita: `instagram_content_publish`,
   `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`.
4. Usa el [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   para generar un token de tu Página con esos permisos, y luego
   conviértelo en un token de larga duración (60 días) siguiendo:
   https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived
5. Obtén tu `META_PAGE_ID` (desde la configuración de tu Página de Facebook) y
   tu `META_IG_USER_ID` (ID de tu cuenta de Instagram Business, lo puedes
   sacar con una consulta `GET /me/accounts` en el Graph API Explorer).

## Paso 3: Credenciales de TikTok

1. Ya tienes tu app creada en https://developers.tiktok.com/ ✅
2. Solicita acceso al **Content Posting API**, scope `video.publish`.
   - Mientras se aprueba, el bot ya puede funcionar en modo "borrador"
     (`MEDIA_UPLOAD`) — solo necesitas el scope básico de publicación, no
     hace falta esperar la aprobación de "Direct Post" para empezar a
     probarlo.
3. Sigue el flujo OAuth de TikTok para obtener un `TIKTOK_ACCESS_TOKEN` de tu
   propia cuenta (con el scope `video.publish` autorizado).
4. Cuando te aprueben "Direct Post" más adelante, avísame o simplemente
   cambia `POST_MODE = "DIRECT_POST"` en `src/post_tiktok.py`.

## Paso 4: Crea las credenciales de Google Cloud (Imagen + Storage)

1. Crea un proyecto en https://console.cloud.google.com
2. Habilita las APIs: "Vertex AI API" y "Cloud Storage API".
3. Crea un bucket de Cloud Storage (público) para alojar las imágenes
   generadas — este será tu `GCS_BUCKET_NAME`.
4. Crea una cuenta de servicio con rol "Vertex AI User" + "Storage Object
   Admin", y descarga su clave en JSON.

## Paso 5: Crea tu cuenta de Anthropic (para los captions)

Genera una API key en https://console.anthropic.com — será tu
`ANTHROPIC_API_KEY`.

## Paso 6: Prueba todo localmente antes de automatizar

```bash
cd src
pip install -r ../requirements.txt
export GCP_PROJECT_ID=tu-proyecto
export GCP_LOCATION=us-central1
export GCS_BUCKET_NAME=tu-bucket
export GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/tu-key.json
export ANTHROPIC_API_KEY=tu-key
export META_PAGE_ACCESS_TOKEN=tu-token
export META_PAGE_ID=tu-page-id
export META_IG_USER_ID=tu-ig-id
export TIKTOK_ACCESS_TOKEN=tu-token

python main.py
```

Revisa que se haya publicado correctamente en las 3 plataformas antes de
pasar al siguiente paso.

## Paso 7: Sube esto a un repositorio de GitHub

```bash
git init
git add .
git commit -m "Bot de publicación automática"
git remote add origin <tu-repo-en-github>
git push -u origin main
```

## Paso 8: Configura los Secrets en GitHub

En tu repo → Settings → Secrets and variables → Actions → "New repository
secret". Crea uno por cada variable de entorno del paso 6 (incluyendo
`GCP_SERVICE_ACCOUNT_JSON` con el contenido completo del JSON de la cuenta de
servicio).

## Paso 9: Listo

El workflow en `.github/workflows/auto-post.yml` ya está programado para
correr 3 veces al día. También puedes lanzarlo manualmente desde la pestaña
"Actions" de tu repo → "Publicación automática en redes sociales" → "Run
workflow", para probar que todo funcione antes de dejarlo en automático.

## Ajustar horarios

Edita los `cron` en `.github/workflows/auto-post.yml`. Los horarios están en
UTC — ajusta según tu zona horaria actual.
