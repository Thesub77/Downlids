from app.models.metadatos import (
    RespuestaMetadatos,
    FormatoVideo,
    TipoFormato,
    Plataforma
)


class MapeoMetadatos:


    def mapear(self, info: dict) -> RespuestaMetadatos:

        return RespuestaMetadatos(
            titulo=self._obtener_titulo(info),
            plataforma=self._obtener_plataforma(info),
            miniatura=self._obtener_miniatura(info),
            duracion=self._obtener_duracion(info),
            autor=self._obtener_autor(info),
            vistas=self._obtener_vistas(info),
            formatos=self._mapear_formatos(info.get("formats", []))
        )

    def _mapear_formato(self, formato: dict) -> FormatoVideo:

        #if not self._validar_formato(formato):
        #    return None

        return FormatoVideo(
            id=self._obtener_id(formato),
            calidad=self._obtener_calidad(formato),
            extension=self._obtener_extension(formato),
            tipo=self._obtener_tipo(formato),
            tamano=self._obtener_tamano(formato)
        )


    def _obtener_id(self, formato: dict) -> str:
        return formato.get("format_id", "")


    def _obtener_calidad(self, formato: dict) -> str:

        tiene_video = formato.get("vcodec") != "none"

        if not tiene_video:
            abr = formato.get("abr")

            if abr:
                return f"{int(abr)} kbps"

            return "Audio"

        return (
            formato.get("format_note")
            or formato.get("resolution")
            or "Desconocida"
        )


    def _obtener_tipo(self, formato: dict) -> TipoFormato:

        tiene_video = formato.get("vcodec") != "none"
        tiene_audio = formato.get("acodec") != "none"

        if tiene_video and tiene_audio:
            return TipoFormato.VIDEO_AUDIO

        if tiene_video:
            return TipoFormato.SOLO_VIDEO

        return TipoFormato.SOLO_AUDIO


    def _obtener_extension(self, formato: dict) -> str:
        return formato.get("ext", "").upper()


    def _obtener_tamano(self, formato: dict) -> str | None:

        bytes_ = (
            formato.get("filesize")
            or formato.get("filesize_approx")
        )

        if not bytes_:
            return None

        return self._formatear_bytes(bytes_)


    def _formatear_bytes(self, bytes_: int) -> str:

        unidades = ["B", "KB", "MB", "GB"]

        tamano = float(bytes_)

        indice = 0

        while tamano >= 1024 and indice < len(unidades) - 1:
            tamano /= 1024
            indice += 1

        return f"{tamano:.1f} {unidades[indice]}"


    def _mapear_formatos(self, formatos: list[dict]) -> list[FormatoVideo]:

        #formatos_validos = []
        videos = []
        audios = []

        for formato in formatos:

            #if not self._validar_formato(formato):
            #    continue

            modelo = self._mapear_formato(formato)

            if modelo.tipo == TipoFormato.SOLO_VIDEO:
                continue
            
            if modelo.tipo == TipoFormato.VIDEO_AUDIO:
                videos.append(modelo)

            elif modelo.tipo == TipoFormato.SOLO_AUDIO:
                audios.append((modelo, formato))

            #formatos_validos.append(
            #    self._mapear_formato(formato)
            #)

        mejor_audio = None

        if audios:
            mejor_audio = max(audios, key=lambda item: item[1].get("abr") or 0)[0]

        resultado = videos

        if mejor_audio:
            resultado.insert(0, mejor_audio)

        return resultado

        #return formatos_validos

    def _obtener_titulo(self, info: dict) -> str:
        return info.get("title", "")


    def _obtener_autor(self, info: dict) -> str:

        return (
            info.get("uploader")
            or info.get("channel")
            or info.get("creator")
            or "Autor desconocido"
        )


    def _obtener_duracion(self, info: dict) -> int:
        return info.get("duration") or 0


    def _obtener_vistas(self, info: dict) -> int:
        return info.get("view_count") or 0


    def _obtener_miniatura(self, info: dict) -> str:
        return info.get("thumbnail", "")


    def _obtener_plataforma(self, info: dict) -> Plataforma:

        extractor = info.get("extractor_key", "").lower()

        if extractor == "youtube":
            return Plataforma.YOUTUBE

        if extractor == "vimeo":
            return Plataforma.VIMEO

        #if extractor == "tiktok":
        #    return Plataforma.TIKTOK

        return Plataforma.DESCONOCIDA
    

    #def _validar_formato(self, formato: dict) -> bool:
    #    return (
    #        #formato.get("vcodec") != "none" and formato.get("acodec") != "none"
    #        formato.get("acodec") != "none"
    #)