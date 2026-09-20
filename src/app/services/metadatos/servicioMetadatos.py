from app.services.metadatos.mapeoMetadatos import MapeoMetadatos
from app.services.metadatos.ytdlpAdaptador import YtdlpAdaptador
from app.services.metadatos.validadorURL import ValidadorURL


class ServicioMetadatos:

    def __init__(self):
        self.adapter = YtdlpAdaptador()
        self.mapper = MapeoMetadatos()
        self.validador = ValidadorURL()

    def obtener_metadatos(self, url: str, plataforma: str | None = None):
        self.validador.validar(url, plataforma)

        informacion = self.adapter.obtener_informacion(url)

        return self.mapper.mapear(informacion)