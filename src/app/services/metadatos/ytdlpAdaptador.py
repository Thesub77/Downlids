import re
import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from app.utils.archivos import eliminar_carpeta_temporal
from app.utils.ffmpeg import obtener_ruta_ffmpeg
from app.core.config import MAX_DOWNLOAD_SIZE_BYTES


def _limpiar_ansi(texto: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]|\[[0-9;]+m', '', str(texto))


class YtdlpAdaptador:

    def _preparar_opciones_cookies(self, opciones: dict, cookies: str | None = None) -> Path | None:
        """
        Configura el soporte de cookies para yt-dlp:
        1. Si se proporcionan cookies (por ejemplo, desde la extensión en formato Netscape),
           se escriben en un archivo temporal.
        2. Si no se proporcionan pero existe un archivo 'cookies.txt' en la raíz del proyecto,
           se utiliza como fallback automático.
        Retorna la ruta del archivo temporal (si fue creado) para su posterior eliminación.
        """
        archivo_temp = None
        if cookies and cookies.strip():
            temp_file = tempfile.NamedTemporaryFile("w", delete=False, suffix="_cookies.txt", encoding="utf-8")
            contenido = cookies.strip()
            if not contenido.startswith("# Netscape"):
                contenido = f"# Netscape HTTP Cookie File\n{contenido}"
            temp_file.write(contenido + "\n")
            temp_file.close()
            archivo_temp = Path(temp_file.name)
            opciones["cookiefile"] = str(archivo_temp)
        else:
            cookiefile_local = Path("cookies.txt")
            if cookiefile_local.is_file():
                opciones["cookiefile"] = str(cookiefile_local.resolve())

        return archivo_temp

    def _normalizar_url(self, url: str) -> str:
        url_limpia = url.strip()
        if not (url_limpia.startswith("http://") or url_limpia.startswith("https://")):
            url_limpia = f"https://{url_limpia}"

        # Soporte para temas / foros de Telegram: t.me/canal/tema_id/mensaje_id -> t.me/canal/mensaje_id
        match_tg_topic = re.match(r'^(https?://(?:t\.me|telegram\.me)/(?!c/)(?:s/)?[^/]+)/\d+/(\d+)(.*)$', url_limpia)
        if match_tg_topic:
            return f"{match_tg_topic.group(1)}/{match_tg_topic.group(2)}{match_tg_topic.group(3)}"

        return url_limpia

    def obtener_informacion(self, url: str, cookies: str | None = None) -> dict:
        url = self._normalizar_url(url)
        es_youtube = "youtube.com" in url or "youtu.be" in url
        opciones = {
            "quiet": True,
            "no_warnings": True,
            "no_color": True,
            "skip_download": True,
            "ffmpeg_location": obtener_ruta_ffmpeg(),
        }
        if es_youtube:
            opciones["extractor_args"] = {
                "youtube": {
                    "player_client": ["default", "android"]
                }
            }

        temp_cookies = self._preparar_opciones_cookies(opciones, cookies)

        try:
            with YoutubeDL(opciones) as ydl:
                informacion = ydl.extract_info(url, download=False)
        except Exception as e:
            mensaje_limpio = _limpiar_ansi(str(e))
            raise Exception(mensaje_limpio) from None
        finally:
            if temp_cookies and temp_cookies.exists():
                try:
                    temp_cookies.unlink()
                except Exception:
                    pass

        if not informacion:
            if "t.me" in url or "telegram.me" in url:
                error_tg = self._obtener_error_telegram(url)
                if error_tg:
                    raise Exception(f"Telegram bloqueó el acceso a este contenido: {error_tg}")
                raise Exception("No fue posible encontrar un video público en el enlace de Telegram. Asegúrate de que el mensaje contenga un video y el canal sea público.")
            raise Exception("No fue posible obtener información del enlace. El contenido no se encuentra disponible o ha sido restringido por la plataforma.")

        return informacion

    def _obtener_error_telegram(self, url: str) -> str | None:
        import urllib.request

        url_limpia = self._normalizar_url(url.strip())
        base_url = url_limpia.split("?")[0]
        embed_url = f"{base_url}?embed=1"
        try:
            req = urllib.request.Request(
                embed_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode("utf-8", errors="replace")

                # 1. Error explícito en el widget de Telegram
                match_err = re.search(r'<div class="tgme_widget_message_error"[^>]*>(.*?)</div>', html, re.DOTALL)
                if match_err:
                    return match_err.group(1).strip()

                # 2. Contenido protegido o no soportado en web embed
                if "message_media_not_supported" in html or "text_not_supported_wrap" in html:
                    return (
                        "El mensaje tiene activada la protección contra copias/guardado ('Restringir guardar contenido' / noforwards) "
                        "o fue compartido como archivo en un tema/foro que Telegram no permite reproducir en la web pública. "
                        "Telegram únicamente permite acceder a este video desde sus aplicaciones oficiales o cliente web directo (MTProto)."
                    )

                # 3. Advertencia de contenido sensible
                match_warn = re.search(r'<div class="tgme_widget_message_warning"[^>]*>(.*?)</div>', html, re.DOTALL)
                if match_warn:
                    return match_warn.group(1).strip()
        except Exception:
            pass
        return None

    def descargar_video(self, url: str, formato: str, hook_progreso=None, cookies: str | None = None) -> str:
        url = self._normalizar_url(url)
        carpeta_temporal = Path(tempfile.mkdtemp())
        postprocessors = []

        if formato == "mp3":
            formato_descarga = "bestaudio/best"
            merge_format = None
            postprocessors = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        elif formato == "bestaudio" or formato in ["140", "251", "249", "250"]:
            formato_descarga = "bestaudio[ext=m4a]/bestaudio"
            merge_format = None
        else:
            # Video: si es adaptativo, yt-dlp combina con bestaudio usando ffmpeg y genera MP4
            formato_descarga = f"{formato}+bestaudio/best"
            merge_format = "mp4"

        es_youtube = "youtube.com" in url or "youtu.be" in url
        opciones = {
            "format": formato_descarga,
            "outtmpl": str(carpeta_temporal / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "no_color": True,
            "ffmpeg_location": obtener_ruta_ffmpeg(),
            "max_filesize": MAX_DOWNLOAD_SIZE_BYTES,
        }

        if es_youtube:
            opciones["extractor_args"] = {
                "youtube": {
                    "player_client": ["default", "android"]
                }
            }

        if merge_format:
            opciones["merge_output_format"] = merge_format

        if postprocessors:
            opciones["postprocessors"] = postprocessors

        if hook_progreso:
            opciones["progress_hooks"] = [hook_progreso]

        temp_cookies = self._preparar_opciones_cookies(opciones, cookies)

        try:
            with YoutubeDL(opciones) as ydl:
                informacion = ydl.extract_info(url, download=True)
                descargas = informacion.get("requested_downloads", [])

                if descargas and descargas[0].get("filepath"):
                    ruta = descargas[0].get("filepath")
                else:
                    archivos = [f for f in carpeta_temporal.iterdir() if f.is_file() and not f.name.endswith(".part")]
                    if not archivos:
                        raise Exception("No hubo archivos descargados.")
                    ruta = str(archivos[0])

                if not Path(ruta).exists():
                    archivos = [f for f in carpeta_temporal.iterdir() if f.is_file() and not f.name.endswith(".part")]
                    if archivos:
                        ruta = str(archivos[0])
                    else:
                        raise Exception("No se encontró el archivo descargado.")

            return ruta
        except Exception as e:
            eliminar_carpeta_temporal(carpeta_temporal)
            mensaje_limpio = _limpiar_ansi(str(e))
            raise Exception(mensaje_limpio) from None
        finally:
            if temp_cookies and temp_cookies.exists():
                try:
                    temp_cookies.unlink()
                except Exception:
                    pass