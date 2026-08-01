from app.services.metadatos.mapeoMetadatos import MapeoMetadatos
from app.services.metadatos.ytdlpAdaptador import YtdlpAdaptador


class ServicioMetadatos:

    def __init__(self):
        self.adapter = YtdlpAdaptador()
        self.mapper = MapeoMetadatos()

    def obtener_metadatos(self, url: str):

        informacion = self.adapter.obtener_informacion(url)

        return self.mapper.mapear(informacion)