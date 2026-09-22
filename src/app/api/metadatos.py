from fastapi import APIRouter, HTTPException

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


@router.post("/metadatos", response_model=RespuestaMetadatos)
def obtener_metadatos(solicitud: SolicitudMetadatos):
    try:
        return servicio.obtener_metadatos(
            str(solicitud.url),
            solicitud.plataforma
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        mensaje = str(e)
        if "members-only" in mensaje or "available to this channel's members" in mensaje:
            detalle = "Este video es exclusivo para miembros del canal y no está disponible públicamente."
        elif "Private video" in mensaje or "video is private" in mensaje:
            detalle = "Este video es privado y no se puede acceder a su contenido."
        elif "Video unavailable" in mensaje or "This video is unavailable" in mensaje:
            detalle = "El video no se encuentra disponible o el enlace no es válido."
        elif any(ig_err in mensaje for ig_err in [
            "Instagram API is not granting access",
            "empty media response",
            "login-required",
            "checkpoint_required",
            "Please log in"
        ]):
            detalle = "Esta publicación o Reel de Instagram es privado o requiere inicio de sesión para acceder."
        else:
            detalle = f"No fue posible obtener los metadatos: {mensaje}"

        raise HTTPException(
            status_code=400,
            detail=detalle
        )