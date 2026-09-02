from app.services.metadatos.ytdlpAdaptador import YtdlpAdaptador


class ServicioDescarga:

    def __init__(self):
        self.adapter = YtdlpAdaptador()

    def descargar(self, url: str, formato: str):

        return self.adapter.descargar_video(
            url=url,
            formato=formato
        )