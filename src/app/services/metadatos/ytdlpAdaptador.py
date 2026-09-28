import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from app.utils.archivos import eliminar_carpeta_temporal
from app.utils.ffmpeg import obtener_ruta_ffmpeg
from app.core.config import MAX_DOWNLOAD_SIZE_BYTES


class YtdlpAdaptador:

    def obtener_informacion(self, url: str) -> dict:
        es_youtube = "youtube.com" in url or "youtu.be" in url
        opciones = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ffmpeg_location": obtener_ruta_ffmpeg(),
        }
        if es_youtube:
            opciones["extractor_args"] = {
                "youtube": {
                    "player_client": ["default", "android"]
                }
            }

        with YoutubeDL(opciones) as ydl:
            return ydl.extract_info(url, download=False)

    def descargar_video(self, url: str, formato: str, hook_progreso=None) -> str:
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
        except Exception:
            eliminar_carpeta_temporal(carpeta_temporal)
            raise