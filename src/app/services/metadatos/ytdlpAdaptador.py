import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from app.utils.archivos import eliminar_carpeta_temporal
from app.utils.ffmpeg import obtener_ruta_ffmpeg


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

    def descargar_video(self, url: str, formato: str):
        carpeta_temporal = Path(tempfile.mkdtemp())

        # Si el usuario seleccionó la opción de sólo audio
        if formato == "bestaudio" or formato in ["140", "251", "249", "250"]:
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
        }

        if es_youtube:
            opciones["extractor_args"] = {
                "youtube": {
                    "player_client": ["default", "android"]
                }
            }

        if merge_format:
            opciones["merge_output_format"] = merge_format


        try:
            with YoutubeDL(opciones) as ydl:
                informacion = ydl.extract_info(url, download=True)
                descargas = informacion.get("requested_downloads", [])

                if not descargas:
                    raise Exception("No hubo archivos descargados.")

                ruta = descargas[0].get("filepath")

                if ruta is None:
                    raise Exception("No se encontró la ruta del archivo.")

            return ruta
        except Exception:
            eliminar_carpeta_temporal(carpeta_temporal)
            raise