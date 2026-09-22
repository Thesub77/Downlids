from pydantic import BaseModel, HttpUrl
from enum import Enum

class Plataforma(str, Enum):
    YOUTUBE = "YouTube"
    TIKTOK = "TikTok"
    INSTAGRAM = "Instagram"
    TWITCH = "Twitch"
    VIMEO = "Vimeo"
    DESCONOCIDA = "Desconocida"

class TipoFormato(str, Enum):
    VIDEO_AUDIO = "Video + Audio"
    SOLO_VIDEO = "Solo video"
    SOLO_AUDIO = "Solo audio"


class SolicitudMetadatos(BaseModel):
    url: HttpUrl
    plataforma: str | None = None


class FormatoVideo(BaseModel):
    id: str
    calidad: str
    extension: str
    tipo: TipoFormato
    tamano: str | None


class RespuestaMetadatos(BaseModel):
    titulo: str
    plataforma: Plataforma
    miniatura: str
    duracion: int
    autor: str
    vistas: int
    formatos: list[FormatoVideo]