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