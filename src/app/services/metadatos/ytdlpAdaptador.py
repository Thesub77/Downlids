import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from app.utils.archivos import eliminar_carpeta_temporal


class YtdlpAdaptador:

    def obtener_informacion(self, url: str) -> dict:

        opciones = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            }
        }

        with YoutubeDL(opciones) as ydl:
            return ydl.extract_info(url, download=False)


    def descargar_video(self, url: str, formato: str):

        carpeta_temporal = Path(tempfile.mkdtemp())

        opciones = {
            "format": formato,
            "outtmpl": str(carpeta_temporal / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            }
        }

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

        