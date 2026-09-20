from app.services.metadatos.ytdlpAdaptador import YtdlpAdaptador
from app.services.metadatos.validadorURL import ValidadorURL


class ServicioDescarga:

    def __init__(self):
        self.adapter = YtdlpAdaptador()
        self.validador = ValidadorURL()

    def descargar(self, url: str, formato: str, plataforma: str | None = None):
        self.validador.validar(url, plataforma)

        return self.adapter.descargar_video(
            url=url,
            formato=formato
        )