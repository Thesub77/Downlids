from urllib.parse import urlparse
from app.models.metadatos import Plataforma


class ValidadorURL:

    DOMINIOS_YOUTUBE = ["youtube.com", "youtu.be"]
    DOMINIOS_TIKTOK = ["tiktok.com", "tiktokv.com"]
    DOMINIOS_INSTAGRAM = ["instagram.com", "instagr.am"]
    DOMINIOS_TWITCH = ["twitch.tv"]
    DOMINIOS_KICK = ["kick.com"]

    def _coincide_dominio(self, host: str, dominios: list[str]) -> bool:
        return any(host == d or host.endswith("." + d) for d in dominios)

    def identificar_plataforma(self, url: str) -> Plataforma:
        url_limpia = url.strip()
        if not (url_limpia.startswith("http://") or url_limpia.startswith("https://")):
            url_limpia = f"https://{url_limpia}"

        parsed = urlparse(url_limpia)
        host = (parsed.hostname or "").lower()

        if self._coincide_dominio(host, self.DOMINIOS_YOUTUBE):
            return Plataforma.YOUTUBE

        if self._coincide_dominio(host, self.DOMINIOS_TIKTOK):
            return Plataforma.TIKTOK

        if self._coincide_dominio(host, self.DOMINIOS_INSTAGRAM):
            return Plataforma.INSTAGRAM

        if self._coincide_dominio(host, self.DOMINIOS_TWITCH):
            return Plataforma.TWITCH

        if self._coincide_dominio(host, self.DOMINIOS_KICK):
            return Plataforma.KICK

        return Plataforma.DESCONOCIDA

    def validar(self, url: str, plataforma_esperada: str | None = None) -> Plataforma:
        url_limpia = url.strip()
        if not url_limpia:
            raise ValueError("La URL no puede estar vacía.")

        plataforma_detectada = self.identificar_plataforma(url_limpia)

        if not plataforma_esperada or plataforma_esperada.strip().lower() in ("auto", "todas"):
            if plataforma_detectada == Plataforma.DESCONOCIDA:
                raise ValueError("La URL no corresponde a ninguna de las plataformas soportadas (YouTube, TikTok, Instagram, Twitch, Kick).")
            return plataforma_detectada

        plataforma_key = plataforma_esperada.strip().lower()

        if plataforma_key in ("youtube", "yt"):
            if plataforma_detectada != Plataforma.YOUTUBE:
                raise ValueError("El enlace proporcionado no coincide con la plataforma seleccionada (YouTube).")
            return Plataforma.YOUTUBE

        elif plataforma_key in ("tiktok", "tt"):
            if plataforma_detectada != Plataforma.TIKTOK:
                raise ValueError("El enlace proporcionado no coincide con la plataforma seleccionada (TikTok).")
            return Plataforma.TIKTOK

        elif plataforma_key in ("instagram", "ig"):
            if plataforma_detectada != Plataforma.INSTAGRAM:
                raise ValueError("El enlace proporcionado no coincide con la plataforma seleccionada (Instagram).")
            return Plataforma.INSTAGRAM

        elif plataforma_key in ("twitch", "tw"):
            if plataforma_detectada != Plataforma.TWITCH:
                raise ValueError("El enlace proporcionado no coincide con la plataforma seleccionada (Twitch).")
            return Plataforma.TWITCH

        elif plataforma_key in ("kick", "kc"):
            if plataforma_detectada != Plataforma.KICK:
                raise ValueError("El enlace proporcionado no coincide con la plataforma seleccionada (Kick).")
            return Plataforma.KICK

        else:
            if plataforma_detectada == Plataforma.DESCONOCIDA:
                raise ValueError(f"Plataforma '{plataforma_esperada}' no soportada.")
            return plataforma_detectada

