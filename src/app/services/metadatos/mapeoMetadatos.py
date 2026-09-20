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

    def _mapear_formatos(self, formatos: list[dict]) -> list[FormatoVideo]:
        audios = []
        videos_por_altura = {}

        for formato in formatos:
            vcodec = formato.get("vcodec")
            acodec = formato.get("acodec")

            # Formatos de solo audio
            if (not vcodec or vcodec == "none") and (acodec and acodec != "none"):
                if formato.get("format_note") != "storyboard" and formato.get("ext") != "mhtml":
                    audios.append(formato)
                continue

            # Formatos de video (con o sin audio)
            if vcodec and vcodec != "none":
                altura = formato.get("height")
                if not altura:
                    resolucion = formato.get("resolution") or ""
                    if "x" in resolucion:
                        try:
                            altura = int(resolucion.split("x")[1])
                        except Exception:
                            altura = None

                if not altura:
                    continue

                tamano = formato.get("filesize") or formato.get("filesize_approx") or 0
                tiene_tamano = 1 if tamano > 0 else 0
                es_mp4 = 1 if formato.get("ext", "").lower() == "mp4" else 0
                es_avc = 1 if "avc" in str(vcodec).lower() else 0
                tbr = formato.get("tbr") or 0

                # Criterio de seleccion: tener tamaño, contenedor MP4, codec H264/AVC, tamaño y bitrate
                puntuacion = (tiene_tamano, es_mp4, es_avc, tamano, tbr)

                if altura not in videos_por_altura or puntuacion > videos_por_altura[altura]["puntuacion"]:
                    videos_por_altura[altura] = {
                        "formato": formato,
                        "puntuacion": puntuacion
                    }

        mejor_audio = None
        bytes_audio = 0
        if audios:
            mejor_audio = max(audios, key=lambda a: a.get("abr") or a.get("tbr") or 0)
            bytes_audio = mejor_audio.get("filesize") or mejor_audio.get("filesize_approx") or 0

        lista_videos = []
        for altura in sorted(videos_por_altura.keys(), reverse=True):
            f = videos_por_altura[altura]["formato"]

            v_bytes = f.get("filesize") or f.get("filesize_approx") or 0
            tiene_audio_propio = bool(f.get("acodec") and f.get("acodec") != "none")

            if tiene_audio_propio:
                bytes_totales = v_bytes
            else:
                bytes_totales = (v_bytes + bytes_audio) if v_bytes else 0

            calidad = self._formatear_etiqueta_calidad(altura)

            lista_videos.append(
                FormatoVideo(
                    id=f.get("format_id", ""),
                    calidad=calidad,
                    extension="MP4",
                    tipo=TipoFormato.VIDEO_AUDIO,
                    tamano=self._formatear_bytes(bytes_totales) if bytes_totales else None
                )
            )

        resultado = lista_videos

        if mejor_audio:
            abr = mejor_audio.get("abr")
            etiqueta_audio = f"Audio ({int(abr)} kbps)" if abr else "Audio"
            ext_audio = mejor_audio.get("ext", "m4a").upper()

            resultado.insert(
                0,
                FormatoVideo(
                    id="bestaudio",
                    calidad=etiqueta_audio,
                    extension=ext_audio,
                    tipo=TipoFormato.SOLO_AUDIO,
                    tamano=self._formatear_bytes(bytes_audio) if bytes_audio else None
                )
            )

        return resultado

    def _formatear_etiqueta_calidad(self, altura: int) -> str:
        if altura >= 2160:
            return f"{altura}p (4K)"
        if altura == 1440:
            return f"{altura}p (2K)"
        if altura == 1080:
            return f"{altura}p (Full HD)"
        if altura == 720:
            return f"{altura}p (HD)"
        return f"{altura}p"

    def _formatear_bytes(self, bytes_: int) -> str:
        unidades = ["B", "KB", "MB", "GB"]
        tamano = float(bytes_)
        indice = 0

        while tamano >= 1024 and indice < len(unidades) - 1:
            tamano /= 1024
            indice += 1

        return f"{tamano:.1f} {unidades[indice]}"

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

        return Plataforma.DESCONOCIDA