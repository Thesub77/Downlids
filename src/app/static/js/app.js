const formulario = document.getElementById("form-metadatos");
const urlInput = document.getElementById("url");
const plataformaSelect = document.getElementById("plataforma-select");

let urlActual = "";
let plataformaActual = "";

if (plataformaSelect) {
    plataformaSelect.addEventListener("change", actualizarPlaceholder);
}

function actualizarPlaceholder() {
    const valor = plataformaSelect.value;
    if (valor === "youtube") {
        urlInput.placeholder = "Pega aquí el enlace de YouTube...";
    } else if (valor === "tiktok") {
        urlInput.placeholder = "Pega aquí el enlace de TikTok (tiktok.com o vm.tiktok.com)...";
    } else if (valor === "instagram") {
        urlInput.placeholder = "Pega aquí el enlace de Instagram (Reel o publicación)...";
    } else if (valor === "twitch") {
        urlInput.placeholder = "Pega aquí el enlace de Twitch (clip o VOD)...";
    } else if (valor === "kick") {
        urlInput.placeholder = "Pega aquí el enlace de Kick (clip o VOD)...";
    } else {
        urlInput.placeholder = "Pega aquí el enlace del video...";
    }
}

function validarCoincidenciaPlataforma(url, plataforma) {
    if (!plataforma || plataforma === "auto") {
        return null;
    }

    let host = "";
    try {
        const urlObj = new URL(url.startsWith("http://") || url.startsWith("https://") ? url : `https://${url}`);
        host = urlObj.hostname.toLowerCase();
    } catch {
        return null; // Dejamos que el backend maneje el formato de URL inválido
    }

    const dominiosYouTube = ["youtube.com", "youtu.be"];
    const dominiosTikTok = ["tiktok.com", "tiktokv.com"];
    const dominiosInstagram = ["instagram.com", "instagr.am"];
    const dominiosTwitch = ["twitch.tv"];
    const dominiosKick = ["kick.com"];

    const esYouTube = dominiosYouTube.some(d => host === d || host.endsWith("." + d));
    const esTikTok = dominiosTikTok.some(d => host === d || host.endsWith("." + d));
    const esInstagram = dominiosInstagram.some(d => host === d || host.endsWith("." + d));
    const esTwitch = dominiosTwitch.some(d => host === d || host.endsWith("." + d));
    const esKick = dominiosKick.some(d => host === d || host.endsWith("." + d));

    if (plataforma === "youtube" && !esYouTube) {
        return "El enlace ingresado no corresponde a YouTube.";
    }

    if (plataforma === "tiktok" && !esTikTok) {
        return "El enlace ingresado no corresponde a TikTok.";
    }

    if (plataforma === "instagram" && !esInstagram) {
        return "El enlace ingresado no corresponde a Instagram.";
    }

    if (plataforma === "twitch" && !esTwitch) {
        return "El enlace ingresado no corresponde a Twitch.";
    }

    if (plataforma === "kick" && !esKick) {
        return "El enlace ingresado no corresponde a Kick.";
    }

    return null;
}

formulario.addEventListener("submit", manejarFormulario);

async function manejarFormulario(event){

    event.preventDefault();

    let url = urlInput.value.trim();
    if(!url){
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        url = `https://${url}`;
    }

    urlActual = url;

    const plataformaSeleccionada = plataformaSelect ? plataformaSelect.value : null;
    plataformaActual = plataformaSeleccionada;

    // Validación en frontend para respuesta instantánea
    const errorValidacion = validarCoincidenciaPlataforma(url, plataformaSeleccionada);
    if (errorValidacion) {
        if (typeof resultado !== "undefined" && resultado) {
            resultado.classList.add("oculto");
        }
        if (typeof limpiarFormatos === "function") {
            limpiarFormatos();
        }
        mostrarMensaje(errorValidacion, "error");
        return;
    }

    const boton = formulario.querySelector("button");

    bloquearBoton(
        boton,
        "Validando URL..."
    );

    try{

        const datos = await obtenerMetadatos(url, plataformaSeleccionada);

        mostrarMensaje(
            "Metadatos obtenidos correctamente.",
            "exito"
        );
        mostrarMetadatos(datos);

        mostrarFormatos(datos.formatos);

        desbloquearBoton(boton);

    }catch(error){
        console.error(error);
        if (typeof resultado !== "undefined" && resultado) {
            resultado.classList.add("oculto");
        }
        if (typeof limpiarFormatos === "function") {
            limpiarFormatos();
        }
        mostrarMensaje(
            error.message || "No fue posible obtener los metadatos.",
            "error"
        );

        desbloquearBoton(boton);

    }

}


