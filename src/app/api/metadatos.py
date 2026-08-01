from fastapi import APIRouter

from app.models.metadatos import (
    SolicitudMetadatos,
    RespuestaMetadatos
)

from app.services.metadatos.servicioMetadatos import ServicioMetadatos

router = APIRouter(
    prefix="/metadata",
    tags=["Metadata"]
)

servicio = ServicioMetadatos()


@router.post("", response_model=RespuestaMetadatos)
async def obtener_metadatos(solicitud: SolicitudMetadatos):
    return servicio.obtener_metadatos(
        str(solicitud.url)
    )