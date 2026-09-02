import tempfile
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp import YoutubeDL

class YtdlpAdaptador:

    def obtener_informacion(self, url: str) -> dict:

        opciones = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True
        }

        with YoutubeDL(opciones) as ydl:
            return ydl.extract_info(url, download=False)


    def descargar_video(self, url: str, formato: str):

        carpeta_temporal = Path(tempfile.mkdtemp())

        opciones = {
            "format": formato,
            "outtmpl": str(Path(carpeta_temporal) / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True
        }


        with YoutubeDL(opciones) as ydl:
            informacion = ydl.extract_info(url, download=True)
            #ruta = ydl.prepare_filename(informacion)
            descargas = informacion.get("requested_downloads", [])

            if not descargas:
                raise Exception("No hubo archivos descargados.")

            ruta = descargas[0].get("filepath")

            if ruta is None:
                raise Exception("No se encontró la ruta del archivo.")

        return ruta

        